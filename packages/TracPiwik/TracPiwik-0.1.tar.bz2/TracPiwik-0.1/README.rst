=======================
Piwik Statistics Plugin
=======================

This plugin will enable your trac environment to be logged by Piwik_. It is
mostly based on the excellent TracGoogleAnalytics_.

.. note:: You need at least Piwik 0.4

To enable the plugin add this to the ``[components]`` section in your ``trac.ini``:

.. sourcecode:: ini

  [components]
  tracpiwik.* = enabled


Configuration
-------------

Mandatory Configuration
~~~~~~~~~~~~~~~~~~~~~~~
 * **Site ID**: Piwik's Site ID. You can find the Site ID either on the
   *Site* tab in Piwik's settings module or in the JavaScript code::

     var piwikTracker = Piwik.getTracker(pkBaseURL + "piwik.php", 1);

   In this example, the Site ID is *1*.

 * **Base URL**: The base URL of your Piwik installation. If the URL of
   your Piwik installation would be ``http://www.example.com/piwik/``, 
   you'd enter ``www.example.com/piwik`` (without ``http://`` and the trailing
   slash).

Advanced Configuration
~~~~~~~~~~~~~~~~~~~~~~
 * **admin_logging**: Disabling this option will prevent all logged in
   ``TRAC_ADMIN``'s from showing up on your Piwik reports.
 * **authenticated_logging**: Disabling this option will prevent all 
   authenticated users from showing up on your Piwik reports.
 * **extensions**: Enter any extensions of files you would like to be tracked
   as a download. For example to track all MP3s and PDFs enter ``mp3|pdf``.
   Outbound link tracking must be enabled for downloads to be tracked.


Download and Install
--------------------

The easiest way to install is using EasyInstall_:

.. sourcecode:: sh

  sudo easy_install TracPiwik


Source Code
-----------

If you wish to be on the bleeding edge and get the latest available code:

.. sourcecode:: sh

  hg clone http://bitbucket.org/piquadrat/tracpiwik/



Bugs and/or New Features
------------------------

Please submit bugs or feature requests to::

  http://bitbucket.org/piquadrat/tracpiwik/issues/


.. _EasyInstall: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _Piwik: http://piwik.org/
.. _TracGoogleAnalytics: http://google.ufsoft.org/wiki/TracGoogleAnalytics
