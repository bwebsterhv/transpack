

# transpack

[Transpack][0] is a file packing and S3 upload app for managing downloaded [transmission][1] files. It allows a user to split and compress (leveraging the systems rar binary) all contents in the downloads/ folder for transmission and then upload these rar files to an AWS S3 bucket.  It is built with [Python][2] using the [Django Web Framework][3].

The platform running Transpack must have a rar library installed, for linux this is typically included in many distros as /usr/bin/.  For Windows you will need a rar binary that supports linux style binary [commands/switches][8] such as the command line tool for [WinRAR][9].

Transpack requires an [AWS][4] account to sync compressed files along with a valid [IAM][5] role with the appropriate level of access to S3.  See the [documentation][0] for detailed instructions.

In addition, Transpack processes compression, upload, and purge requests as background tasks using [arteria/django-background-tasks][6].  See the [documentation][0] for recommendations on how to both execute and manage these tasks.

Transpack was built using the [arocks/Edge][7] project skeleton.

## Installation

### Quick start

To set up a development environment quickly, first install Python 3. It
comes with virtualenv built-in. So create a virtual env by:

    1. `$ python3 -m venv transpack`
    2. `$ . transpack/bin/activate`

Install all dependencies:

    pip install -r requirements.txt

Create and configure a local environment settings file from the skeleton:

    cp transpack/settings/local.sample.env transpack/settings/local.env
    nano transpack/settings/local.env

Run migrations:

    python manage.py migrate

Create a super user:

    python manage.py createsuperuser

Verify tests pass:

    python manage.py test

Begin processing background tasks:

    python manage.py process_tasks

### Detailed instructions

Take a look at the [docs][0] for more information.

[0]: https://www.google.com/
[1]: https://transmissionbt.com
[2]: https://www.python.org/
[3]: https://www.djangoproject.com/
[4]: https://aws.amazon.com/
[5]: https://aws.amazon.com/iam/
[6]: https://github.com/arteria/django-background-tasks
[7]: https://github.com/arocks/edge/
[8]: https://ss64.com/bash/rar.html
[9]: http://www.rarlab.com/