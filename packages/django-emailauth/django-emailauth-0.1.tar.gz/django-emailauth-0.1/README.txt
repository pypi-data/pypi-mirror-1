================================
Django user email authentication
================================


This is a Django application providing all essentials for authenticating users
based on email addresses instead of usernames.

This application can operate in a traditional one user - one email mode as
well as one user - many emails mode. And I plan to add EAUT and OpenID support
to this mode eventually.

This application consists of:

* UserEmail model

* Views and forms:

  - Login;
  - Password reset;
  - Account management:

    - User registration and email confirmation;
    - Adding and removing emails to/from existing user accounts;
    - Changing default emails
    - Changin email (for single email mode)

* Authentication backends:

  - Email backend for authenticating users who has UserEmail object (regular
    site users);
  - Fallback backend for users without such objects (most likely that will be
    site administration)


Motivation for this application
-------------------------------

For some reason I was lucky to work on projects which required email-based
authentication, and one of these projects could benefit if users could have
several emails.

To solve basic authentication problem I quickly came up with this:
http://www.djangosnippets.org/snippets/74/

That trick works but it has several drawbacks:

* It breaks standard Django tests, so when you run python manage.py test on
  your project you'll have to filter out error messages from broken Django
  tests. Not good.

* Standard Django login view can't handle long (longer than 30 characters)
  email addresses.

* If you put email verification status and all such into UserProfile class you
  tie code working with emails to your project impairing code reuse.


To solve above problems I decided to create this application. It stores all
email-specific data into UserEmail model (verification code, code creation
date, verification status etc.) So this application manages all email-related
data, not messing with UserProfile and saves application user from reinventing
the wheel.


Example project
---------------

To see this application in action::

    cd emailauth/example
    python manage.py syncdb
    python manage.py runserver

Please bear in mind that all emails sent by example project are not actually
sent but printed to stdout instead.

To see how traditional one user - one email mode works::

    cd emailauth/example
    python manage.py syncdb
    python manage.py runserver --settings=settings_singleemail


Configuration
-------------

Emailauth uses following configuration vairables:

* ``EMAILAUTH_USE_SINGLE_EMAIL`` (default False) - selects between one user - one
  email and one user many email mode.

* ``EMAILAUTH_VERIFICATION_DAYS`` (default 3) - how long will email
  verification codes work


Maintenance
-----------


Emailauth provides ``cleanupemailauth`` manage.py command which removes
expored UserEmail objects and inactive users associated with epxired UserEmail
objects.

You might want to run it occasionally.


Future plans
------------

* Add EAUT and OpenID support so this application could be used for OpenID
  authentication and switch to emails for users without OpenID
