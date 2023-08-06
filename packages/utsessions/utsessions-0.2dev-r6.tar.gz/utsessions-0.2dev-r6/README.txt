Introduction
============

*utsessions* allow the features of timed and unique sessions for an user
account in Django.

What does it do ?
=================

*utsessions* is a middleware that makes all opened user sessions unique.

When an user session is opened, the user account can't be reused
before a certain amount of time. After this time, if the user account
is reused, the first session is closed and a second one is opened.

A session can also be automaticaly closed after a choosen time.

This kind of behavior is useful for websites providing access to data
by unique user account.

Philosophy
==========

*utsessions* was written to be easily :

 * Installed in your projects, by simply registering the middleware.
 * Extended thanks to his design in object: each component can be removed or reused.
 * Configured, with the settings.py file which allows different behaviors.

Installation
============

Download the latest packaged version at http://code.google.com/p/django-ut-sessions/ 
and unpack it.

You can also perform a Subversion checkout to get the latest code. ::

  svn checkout http://django-ut-sessions.googlecode.com/svn/trunk/ django-ut-sessions

Inside the package use this command line to install the package into
your PYTHONPATH. ::

 $> python setup.py install

Project installation
====================

Now simply add this following line into your *MIDDLEWARE_CLASSES* section. ::

  utsessions.middleware.UTSessionMiddleware

It must be after the SessionMiddleware and AuthentifcationMiddleware
like this : ::

  MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'utsessions.middleware.UTSessionMiddleware',
  )

Settings
========

If you want to define the period of a session before being logged out,
set a value in seconds to *SESSION_LIMIT_SECONDS* in your settings.py

A session can be released for another user before a certain amount of
time, set to default at 300 seconds. To change this value define
*SESSION_TOKEN_LIMIT_SECONDS*. If set to 0, no lock will be created.

Tests
=====

Put utsessions into your *INSTALLED_APPS* section and run : ::

  $> python manage.py test utsessions
