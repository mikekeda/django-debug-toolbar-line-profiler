=======================================
Django Debug Toolbar Line Profile Panel
=======================================

.. image:: https://api.codacy.com/project/badge/Grade/27b4fb9c7d3c46abb7dac9a06d16698e
   :alt: Codacy Badge
   :target: https://app.codacy.com/manual/mikekeda/django-debug-toolbar-line-profiler?utm_source=github.com&utm_medium=referral&utm_content=mikekeda/django-debug-toolbar-line-profiler&utm_campaign=Badge_Grade_Dashboard

.. image:: https://requires.io/github/mikekeda/django-debug-toolbar-line-profiler/requirements.svg?branch=master
     :target: https://requires.io/github/mikekeda/django-debug-toolbar-line-profiler/requirements/?branch=master
     :alt: Requirements Status

The `Django Debug Toolbar 
<https://github.com/mikekeda/django-debug-toolbar-line-profiler>`_ is a configurable set of panels that display various
debug information about the current request/response and when clicked, display
more details about the panel's content.

This package provides a panel that incorporates output from line_profiler_

This panel will only function with django_debug_toolbar>=1.0, before that it's functionality
was contained in the debug_toolbar.panels.profiling.ProfilingPanel.

This Django Debug Toolbar panel is released under the BSD license, like Django
and the Django Debug Toolbar. If you like it, please consider contributing!

The Django Debug Toolbar was originally created by Rob Hudson
in August 2008 and was further developed by many contributors.

.. _line_profiler: http://pythonhosted.org/line_profiler/


Installation
============

To install the line_profiler panel, first install this package with ``pip install django-debug-toolbar-line-profiling``, then add debug_toolbar_line_profiler to the INSTALLED_APPS::

    INSTALLED_APPS = (
        ...
        'debug_toolbar_line_profiler',
    )

and add the panel to DEBUG_TOOLBAR_PANELS::

    DEBUG_TOOLBAR_PANELS = (
        ...
        'debug_toolbar_line_profiler.panel.ProfilingPanel',
    )

Configuration
=============

By default, the panel will profile your view function. If you use class based views
the panel will profile all functions on the class that don't start with _. If you
want additional code to be profiled, add the @profile_additional decorator like so::

    from debug_toolbar_line_profiler import profile_additional
    from boto.s3.connection import S3Connection
    
    ...
    
    @profile_additional(S3Connection.make_request)
    def your_view_code(*args, **kwargs):
        ...

Signals
=======

There is also a signal (debug_toolbar_line_profiler.signals.profiler_setup) that
you can attach to for integrating class based views like django rest framework.

Here is an example::

    from rest_framework.viewsets import ViewSet
    from rest_framework.response import Response
    from debug_toolbar_line_profiler import signals


    class AViewSet(ViewSet):
        def list(self, request):
            return Response([])

        def retrieve(self, request, pk=None):
            return Response({})


    def register_profile_views(sender, profiler, **kwargs):
        profiler.add_function(AViewSet.list)
        profiler.add_function(AViewSet.retrieve)


    signals.profiler_setup.connect(register_profile_views,
                                   dispatch_uid='register_profile_views')
