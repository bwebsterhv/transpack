from background_task import background
from django.conf import settings

from pathlib import Path
from librar import archive
from botocore.exceptions import ClientError
import boto3
import shutil
import hashlib
import base64
import os
import logging

logger = logging.getLogger("project")


@background(schedule=3)
def pack_folder(folder, filename, silent=True):
    """ Task to pack (librar) folder contents """
    base_dir = settings.TRANSMISSION_DOWNLOAD_DIR
    folder_path = "{}{}".format(base_dir, folder)
    archive_folder = "{}/{}".format(folder_path, filename)
    archive_file = "{}/{}.rar".format(archive_folder, filename)
    folder_hash = hashlib.md5(folder.encode('utf-8')).hexdigest()

    # Check for packing flag, if found skip task
    packing_file = "{}/{}.packed".format(folder_path, folder_hash)
    packing_flag_set = os.path.exists(packing_file)
    logger.info("Kickoff packing job: {}".format(archive_file))
    if not packing_flag_set:
        # Touch file to kick off packing
        Path(packing_file).touch()

        # Create folder for archive
        if not os.path.exists(archive_folder):
            os.makedirs(archive_folder)

        # Initiate archive
        trans_archive = archive.Archive(archive_file, archive_folder, settings.RAR_BINARY_PATH)
        trans_archive.set_exclude_base_dir(True)
        trans_archive.add_dir(folder_path)
        trans_archive.exclude(packing_file)
        trans_archive.exclude(archive_folder)
        trans_archive.set_compression_level(settings.ARCHIVE_COMPRESSION_LEVEL)
        trans_archive.set_recovery_record(settings.ARCHIVE_RECOVERY_RECORD)
        trans_archive.set_volume_size(settings.ARCHIVE_SPLIT_SIZE)
        trans_archive.run(silent)

        # Set archive complete flag
        with open(packing_file, "a") as myfile:
            myfile.write(filename)

        # Done, log
        logger.info("Packed: {}".format(folder_path))

@background(schedule=3)
def upload_folder(folder):
    """ Task to upload to S3 packed folder contents """
    base_dir = settings.TRANSMISSION_DOWNLOAD_DIR
    folder_path = "{}{}".format(base_dir, folder)
    folder_hash = hashlib.md5(folder.encode('utf-8')).hexdigest()

    # Validate packing flag and file with archive name
    packing_file = "{}/{}.packed".format(folder_path, folder_hash)
    if not os.path.exists(packing_file):
        raise Exception("*** FATAL ERROR | upload_folder *** - \
                         Packing flag not found: {}".format(packing_file))

    with open(packing_file, 'r') as archive_info:
        archive_name = archive_info.read()

    archive_folder = "{}/{}".format(folder_path, archive_name)
    if not os.path.exists(archive_folder):
        raise Exception("*** FATAL ERROR | upload_folder *** - \
                         Archive folder not found: {}".format(archive_folder))

    client = boto3.client('s3')
    # Touch file to kick off uploading
    uploading_file = "{}/{}.uploaded".format(folder_path, folder_hash)
    uploaded_files = []
    Path(uploading_file).touch()

    # enumerate archive files recursively
    for (root, dirs, files) in os.walk(archive_folder):
        for filename in files:
            archive_file = "{}/{}".format(archive_folder, filename)
            s3_path = "{}/{}".format(archive_name, filename)
            # Check if file already exists, skip if so
            try:
                client.head_object(Bucket=settings.TRANSMIT_S3_BUCKET, Key=s3_path)
                logger.info("Skipping {}, already exists on s3.\n".format(s3_path))
            except ClientError as e:
                logger.info("Upload {} to S3 as {}...\n".format(archive_file, s3_path))
                try:
                    client.upload_file(archive_file, settings.TRANSMIT_S3_BUCKET, s3_path)
                except ClientError as e:
                    logger.error("*** ERROR | upload_folder *** - \
                                  Archived file {} failed to upload to s3, \
                                  got\n{}\n".format(archive_file, e))

                # Set ACL to public
                client.put_object_acl(ACL='public-read',
                                      Bucket=settings.TRANSMIT_S3_BUCKET,
                                      Key=s3_path)

                # Record keeping
                uploaded_files.append(filename)

    # Set uploading file details
    with open(uploading_file, "a") as myfile:
        myfile.write("\n".join(uploaded_files))

@background(schedule=3)
def delete_folder(folder):
    """ Task to delete both S3 folder and all local folder contents """
    client = boto3.client('s3')
    base_dir = settings.TRANSMISSION_DOWNLOAD_DIR
    folder_path = "{}{}".format(base_dir, folder)
    folder_hash = hashlib.md5(folder.encode('utf-8')).hexdigest()

    # Set delete flag
    delete_file = "{}/{}.purge".format(folder_path, folder_hash)
    Path(delete_file).touch()

    # Validate packing flag and file with archive name
    archive_name = ""
    packing_file = "{}/{}.packed".format(folder_path, folder_hash)
    if os.path.exists(packing_file):
        with open(packing_file, 'r') as archive_info:
            archive_name = archive_info.read()

    logger.info("Purge check for archive {}...\n".format(archive_name))
    if archive_name != "":
        # Purge from S3, query S3 folder to get all keys
        objects_to_delete = []
        keys = client.list_objects(
            Bucket=settings.TRANSMIT_S3_BUCKET,
            Prefix="{}/".format(archive_name)
        )['Contents']

        for key in keys:
            objects_to_delete.append({'Key': key['Key']})

        logger.info("Purge from S3: \n{}\n".format(objects_to_delete))
        try:
            client.delete_objects(
                Bucket=settings.TRANSMIT_S3_BUCKET,
                Delete={'Objects': objects_to_delete}
            )
        except ClientError as e:
            logger.error("SILENT ERROR | delete_folder - \
                         Tried to remove archive {} from S3 and got\n{}\n".format(archive_name, e))

    # Purge files on disk
    logger.info("Remove directory tree {}...\n".format(folder_path))
    shutil.rmtree(folder_path)
