:Author: John Millikin
:Copyright: This document has been placed in the public domain.

Overview
========

``django-resourcetags`` is a set of utility functions and tags for Django.
It simplfies inclusion of static resources into a page, by providing
auto-versioning and transparent compression handling.

Usage
=====

Include ``django_resourcetags`` in your ``INSTALLED_APPS`` setting. Load
the tag library with ``{% load resources %}``, and then use the
``resource``, ``resource_group``, or ``resource_url`` tags.

``resource_url``
----------------

Used like ``{% resource_url "/myapp/somefile.txt" %}``. Will calculate
the mtime of the resource and include it in the URL, to implement
auto-versioned resources. The final URL will be of the form::

    {{MEDIA_URL}}/{{file_mtime}}/myapp/somefile.txt

When finding the mtime, file paths are relative to ``MEDIA_ROOT``. If the
file cannot be found, an mtime of 0 will be used.

``resource``
------------

Used like ``{% resource "/myapp/somefile.txt" %}``. Autodetects the
MIME-type of the resource and wraps the URL in an appropriate HTML tag.
Default handlers exist for CSS, JavaScript, PNG, JPEG, and GIF. Additional
handlers may be registered in the ``RESOURCE_HANDLERS`` setting, with this
format::

    RESOURCE_HANDLERS = {'text/css': 'myproject.myapp.resource_handlers.css'}

``resource_group``
------------------

Used like ``{% resource_group "mygroup" %}``. Groups may be defined in
the settings file to reduce duplicated typing and facilitate compression
(see below). Resource groups are defined in the format::

    RESOURCE_GROUPS = {'mygroup': ('file1.css','file2.css')}

In non-compressed mode, each file will be included in a separate tag.

Compression
===========

Resources and resource groups may be compressed using the command
``manage.py compressresources``. Resource groups will be concatenated
together into one file, and run through a compression filter. Single
resources may also be run through the compression filter by listing
them in the ``COMPRESS_EXTRA`` setting.

Compression filters are functions listed in the ``RESOURCE_COMPRESSION_FILTERS``
setting, which is a mapping of MIME-type -> [function names]. Compression
functions are called in sequence.

Compressed resources are stored in the directory specified by
``COMPRESSED_MEDIA_ROOT``, and served from the URL ``COMPRESSED_MEDIA_URL``.

Compression filters for CSS and JavaScript are included in the
``django_resourcetags.compression.filters`` module, under the names
``filters.javascript`` and ``filters.css``.

Genshi Integration
==================

For use with ``django-genshi``. Include ``django_resourcetags.genshi_integration.template_context``
in your ``TEMPLATE_CONTEXT_PROCESSORS`` setting, and you will have access
to the functions ``resource()``, ``resource_group()``, and ``resource_url()``.
These functions work just like the template tag equivalents.
