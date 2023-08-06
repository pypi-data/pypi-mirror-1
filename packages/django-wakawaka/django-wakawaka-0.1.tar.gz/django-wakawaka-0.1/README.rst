===============
django-wakawaka
===============

django-wakawka is a super simple wiki system written in Python using the Django
framework.

Installation:
=============

1. Put ``wakawaka`` to your INSTALLED_APPS in your settings.py within your
   django project.
2. Add (r'^wiki/', include('wakawaka.urls')), to your urls.py.

That's all. Wakawaka has no other dependencies than Django 1.0 (or Django 1.1,
currently known as *trunk*)

Configuration:
==============

Wakawaka takes care of Django's permission system. Grant your users always a
pair of ``wikipage`` and ``revision`` permissions either what they should do.
(Adding, changing or deleting WikiPages)

Optional Configuration:
-----------------------

The name of your first wiki page is defined as ``WikiIndex``. You can change
this by adding a setting ``WAKAWAKA_DEFAULT_INDEX`` to your settings.py.
Example::

    WAKAWAKA_DEFAULT_INDEX = 'Home'

Words that are written in CamelCase (a pair of one upper letter followed by
*n* lower letters) are automatically treated as internal wiki link. You can
change this behaviour by adding a setting ``WAKAWAKA_SLUG_REGEX`` in your
settings.py. This holds a regular expression of the wiki urls. Default::

    WAKAWAKA_SLUG_REGEX = r'((([A-Z]+[a-z]+){2,})(/([A-Z]+[a-z]+){2,})*)'

Attachments:
============

Wakawaka does not provide the ability to store file attachments to wiki pages.
To do so, have a look on the side project `django-attachments`_ which provides
a unobstrusive way to add attachments to models.

.. _`django-attachments`: http://github.com/bartTC/django-attachments/