********
Overview
********

Here you will find a high level overview of the purpose and archetecture of 
the Transpack application.

=======
Purpose
=======

Torrenting is so darn useful and client software such as 
`Transmission <https://transmissionbt.com/>`_ with daemon support and a 
web-client make it a snap to easily bittorrent away from draconian ISPs, 
restrictive networks, and off-premise locations.  However, once those files 
are downloaded you have to decide how you are going to aquire them.

File Transfer Thoughts
======================

Sure, you can sFTP to the server, but you will find it painfully slow due to 
the overhead of openssh.  FTP?  
`Not secure by any means <https://www.quora.com/Why-is-FTP-called-unsafe>`_.  
`FTPS? <https://en.wikipedia.org/wiki/FTPS>`_ Much better on the security 
side than FTP, but still has overhead and its passive port range might 
not be firewall configuration friendly.

An `NFS <https://en.wikipedia.org/wiki/Network_File_System>`_ share can be 
very convienient once configured and mounted locally, but can be quite 
daunting to deploy and maintain (and secure!).  

Cloud storage solutions such as 
`Dropox <https://www.dropbox.com/help/syncing-uploads/sync-overview>`_ or 
`Google Drive <https://www.google.com/drive/>`_ have clients that can indeed 
sync folders relatively easily, but may cost you depending on the size of 
your files.

`Amazon S3 <https://aws.amazon.com/s3/>`_.  

Placeholder about the transpack solution


===============
Core Components
===============
Placeholder about the core building blocks of the app

Django Edge
===========
Placeholder about the project structure: Edge

Background Tasks
================
Placeholder on background task processing

Notes for Deployment
--------------------
Placeholder for deploying the processing management command, supervisor

====================
Application Overview
====================
Placeholder about the application itself

Browse
======
Placeholder on browsing the core downloaded files & web interface

Packing
=======
Placeholder on packaging the files

Librar
------
Placeholder on librar notes

Uploading
=========
Placeholder on uploading packaged files to S3

Amazon S3
---------
Placeholder on Amazon S3

Purging
=======
Placeholder on removing packaged files from S3 and disk
