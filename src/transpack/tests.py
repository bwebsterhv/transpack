from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.crypto import get_random_string
from pathlib import Path
import os
import shutil
import time
import stat


class TranspackViewTests(TestCase):
    """ Tests of the transpack app """

    def setUp(self):
        """ Run for every test case """
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(email='testuser@test.com', password='s3cR$t')

    @classmethod
    def setUpClass(cls):
        """ Create dummy folder and file, we don't need to execute this on every
            test run, only one time."""
        super(TranspackViewTests, cls).setUpClass()
        cls.test_folder = get_random_string(length=32)
        cls.test_file = "{}.dummy".format(get_random_string(length=32))

        # Create testing folder & file
        test_folder_path = "{}{}".format(settings.TRANSMISSION_DOWNLOAD_DIR, cls.test_folder)
        if not os.path.exists(test_folder_path):
            os.makedirs(test_folder_path)

        # Set some dummy content
        test_file_path = "{}/{}".format(test_folder_path, cls.test_file)
        with open(test_file_path, "a") as myfile:
            myfile.write(get_random_string(length=4096))

    def test_pages_are_auth_protected(self):
        """
        Verify that internal pages require valid auth session and redirect to login with
        breadcrumbs back to the origin request
        """
        protected_pages = ('browse',)
        protected_ajax_gets = ('get_s3_files', 'get_local_files',)
        protected_ajax_posts = ('runtask_pack', 'runtask_upload', 'runtask_delete',)

        # Standard page checks
        for protected_page in protected_pages:
            response = self.client.get(reverse(protected_page))
            redir_url = '{}?next={}'.format(reverse('accounts:login'), reverse(protected_page))
            self.assertRedirects(response, redir_url)

        # AJAX GET request checks
        for protected_ajax_get in protected_ajax_gets:
            response = self.client.get(
                reverse(protected_ajax_get),
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            self.assertEquals(response.status_code, 403)

        # AJAX POST request checks
        for protected_ajax_post in protected_ajax_posts:
            response = self.client.post(
                reverse(protected_ajax_post),
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            self.assertEquals(response.status_code, 403)

    def test_can_login(self):
        """
        Verify a user can login
        """
        self.client.login(username='testuser@test.com', password='s3cR$t')
        response = self.client.get(reverse('browse'), follow=True)
        self.assertEquals(response.status_code, 200)

    def test_browse_has_test_folder(self):
        """
        Verify the test folder exists in the /browse page
        """
        self.client.login(username='testuser@test.com', password='s3cR$t')
        response = self.client.get(reverse('browse'))
        self.assertContains(response, self.test_folder)

    def test_transpack_operations(self):
        """
        1 - Invokes a pack_folder task to run immediately to verify we can
            compress (via librar) the test data
        2 - Invokes a upload_folder task to run immediately to verify we can
            upload (via Boto) the test folder to S3
        3 - Invokes a delete_folder task to run immediately to verify we can
            purge both the data on S3 and test files on disk
        """
        from transpack.tasks import pack_folder, upload_folder, delete_folder
        packing_folder_path = "{}{}/{}".format(
            settings.TRANSMISSION_DOWNLOAD_DIR,
            self.test_folder,
            "TEST"
        )
        # Pack test
        pack_folder.now(self.test_folder, "TEST")
        self.assertTrue(os.path.exists(packing_folder_path))

        # Upload test
        upload_folder.now(self.test_folder)

        # Purge test
        delete_folder.now(self.test_folder)
