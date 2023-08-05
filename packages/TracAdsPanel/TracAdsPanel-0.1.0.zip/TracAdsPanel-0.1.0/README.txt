TracAdsPlugin
=============

TracAdsPlugin_ is of course a trac_ plugin designed to display ads on your
trac_ environment.

The main feature of the plugin is that it allows the user to persistently_
hide the ads, making your trac_ environment less annoying to those who
dislike ads and supporting open-source projects through them.

Installation
------------
Installing the plugin is as easy as::

  sudo easy_install TracAdsPlugin

And then enabling it:

.. sourcecode:: ini

  [components]
  adsplugin.* = enabled

And that's it!

Now, all you have to do is to go to the administration and under **Ads Panel**
you have a configuration link to setup the plugin.

**Note**: For up-to-date documentation please visit TracAdsPlugin_'s site.

~~~~

.. [persistently] *The user choice of hiding the ads will remain untouched
                  throughout it's later visits, and he'll still have the
                  choice to display them again*.

.. _trac: http://trac.edgewall.org
.. _TracAdsPlugin: http://devnull.ufsoft.org/wiki/TracAdsPanel
