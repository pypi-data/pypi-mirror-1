Installation
============

Install the ``django-templatequery`` package from the Python Package Index with
one of the following commands::

    easy_install django-templatequery

*or*::

    pip intall django-templatequery

If you want to use the templatetags that come with **django-templatequery** you
need to put ``'django_templatequery'`` to the end of your ``INSTALLED_APPS``
setting.

Please note: It maybe is a risk to make the templatetags available for template
designers. It is possible that they have access to models which they shouldn't
have. Only do this if you trust the people that work on your templates!

Usage
=====

*to be written ...*

Playing around
==============

If you just want to play around with the code without installing in your system
or using in a real project you can follow the commands below. It will install
everything

Start coding
============

In the case you want to contribute to the code I recommend the following steps:

    1. Get a copy of the development repository from launchpad with ``bzr branch
    lp:django-templatequery``
    2. cd into the branch directory
    3. Run ``python bootstrap.py`` and ``python bin/buildout`` (this will setup
    the development 
