README for the 'browser/javascripts/' directory
===============================================

This folder is a Zope 3 Resource Directory acting as a repository for
javascripts.

Its declaration is located in 'browser/configure.zcml':

    <!-- Resource directory for javascripts
      See ./browser/javascripts/README.txt
      for more information about registering javascripts as Zope 3 browser
      resources.
      -->
    <browser:resourceDirectory
        name="collective.portlet.googleapps.javascripts"
        directory="javascripts"
        layer=".interfaces.IThemeSpecific"
        />

A javascript placed in this directory (e.g. 'swfobject.js') can be accessed from
this relative URL:

    "collective.portlet.googleapps.javascripts/swfobject.js"

Note that it might be better to register each of these resources separately if
you want them to be overridable from zcml directives.

The only way to override a resource in a resource directory is to override the
entire directory (all elements have to be copied over).

A Zope 3 browser resource declared like this in 'browser/configure.zcml':

    <browser:resource
        name="main.js"
        file="javascripts/main.js"
        layer=".interfaces.IThemeSpecific"
        />

can be accessed from this relative URL:

    "++resource++main.js"

Notes
-----

* Javascripts registered as Zope 3 resources might be flagged as not found in
  the 'portal_javascripts' tool if the layer they are registered for doesn't match the
  default skin set in 'portal_skins'.
  This can be confusing but it must be considered as a minor bug in the JavaScripts
  registry instead of a lack in the way Zope 3 resources are handled in
  Zope 2.

* Customizing/overriding javascripts that are originally accessed from the
  'portal_skins' tool (e.g. Plone default javascripts) can be done inside that
  tool only. There is no known way to do it with Zope 3 browser resources.
  Vice versa, there is no known way to override a Zope 3 browser resource from
  a skin layer in 'portal_skins'.
