from setuptools import setup, find_packages
import sys, os

version = '0.1.1'

setup(name='pulse',
      version=version,
      description="Simple scheduling WSGI middleware.",
      long_description="""\
Scheduling WSGI Middleware
============================

This package acts as a WSGI scheduling engine, the middleware can be configured
to request web contexts at given intervals.  A user may then, within their application,
configure the web contexts to perform scheduled tasks e.g. maintainence.

The middleware for pulse is provided in pulse.middleware:PulseMiddleware and a paste
filter_app_factory is also provided.

Configuration
-----------------
Pulse can be configured in two ways.  The Middleware takes keyword configuration
arguments when constructed,or alternatively a config dictionary 
allowing it to be configured by paste.
If using pastes the pulse configuration options take the form of:
pulse.config.$configoption.

Currently only one configuration option is supported:
* context - This is the base web context that tasks are sent to,
    tasks are dispatched to /$context/$action, unless action is an absolute
    path.
* mode - This specifies the multiprocessing mode, the default is 'theading',
    if running python2.6 the 'processing' option is also available.
* guard - If True the pulse middleware prevents any pulse managed contexts
    from being accessed extenally, the default is False.

Tasks
------
Each task defines at an interval and a web context, pulse will request
the specified web context every interval seconds.

Creating A Task
~~~~~~~~~~~~~~~~
A new task is created by specifying configuration options, each option takes the form:
pulse.task.$taskname.$option

The following task configuration options are available:
* interval - The interval between task dispatching.
* action - The action to dispatch to: see pulse.config.context

Tasks can also be programmatically configured by passing a dictionary of 
<taskname, TaskObject> into  PulseMiddleware's task keyword argument.

Example
========

To request the following context '/sessions/cleanup' every 5 minutes, the following
paste configuration could be used:

pulse.config.context = sessions

pulse.task.cleanup.action = cleanup
pulse.task.cleanup.interval = 300
""",
      classifiers=['Topic :: Internet :: WWW/HTTP :: WSGI'], 
        # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Sam Rayment',
      author_email='',
      url='',
      license='MIT Licence',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "WebOb>=-0.9.6",
          "PasteDeploy>=1.3.3",
      ],
      entry_points="""
        [paste.filter_app_factory]
        pulse_factory = pulse.middleware:pulse_filter_app_factory
      """,
      )
