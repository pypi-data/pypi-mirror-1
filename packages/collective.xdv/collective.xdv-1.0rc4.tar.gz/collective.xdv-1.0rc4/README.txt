============
Introduction
============

This package services for applying a transformation to Plone's HTML output,
using the XDV compiler. XDV is an implementation of Deliverance, specifically
the original Deliverance XML-based syntax. It works by compiling the theme
(an HTML file) and rules (an XML file) into a single XSLT file, which is then
applied to Plone's HTML on render.

collective.xdv uses a post-publication hook made available through the
plone.postpublicationhook package to modify the request as it is is sent
to the browser. If you are using repoze.zope2 or another WSGI-based solution
for hosting Zope, it may be better to simply apply the transform in the
WSGI pipeline, using dv.xdvserver (on which this package depends). However,
for a standard Plone 3.x, this package provides a tightly integrated solution.

Dependencies
------------

collective.xdv depends on:

  * plone.registry and plone.app.registry to manage settings
  * plone.autoform, plone.z3cform and plone.app.z3cform to render the 
    control panel
  * dv.xdvserver to compile the XDV theme
  * lxml to perform the final transform

These will all be pulled in automatically if you are using zc.buildout and follow the installation instructions.

Installation
------------
To install collective.xdv into your Plone instance, locate the file buildout.cfg in the root of your Plone instance directory on the file system, and open it in a text editor. Locate the section that looks like this::

	# extends = http://dist.plone.org/release/3.3/versions.cfg
	extends = versions.cfg
	versions = versions

It may also have a URL in the "extends" section, similar to the commented-out first line, depending on whether you pull the Plone configuration from the network or locally.

To add collective.xdv to our setup, we need some slightly different versions of a couple of the packages, so we extend the base config with a version list from the good-py service, so change this part of the configuration so it looks like this::

	extends = versions.cfg
          	  http://good-py.appspot.com/release/collective.xdv/1.0
	versions = versions

What happens here is that the dependency list for collective.xdv specifies some new versions for you via the good-py URL. This way, you don't have to worry about getting the right versions, Buildout will handle it for you.

Next step is to add the actual collective.xdv add-on to the "eggs" section of buildout.cfg. Look for the section that looks like this::

	eggs =
    	Plone

This section might have additional lines if you have other add-ons already installed. Just add the collective.xdv on a separate line, like this::

	eggs =
    	Plone
    	collective.xdv [Zope2.10]

Note the use of the [Zope2.10] extra, which brings in the ZPublisherEventsBackport package for forward compatibility with Zope 2.12 / Plone 4.

Note that there is no need to add a zcml slug as collective.xdv uses z3c.autoinclude.

Once you have added these lines to your configuration file, it's time to run Buildout, so the system can add and set up collective.xdv for you. Go to the command line, and from the root of your Plone instance (same directory as buildout.cfg is located in), run Buildout like this::

	$ bin/buildout

You will see output similar to this::

	Getting distribution for 'collective.xdv==1.0'.
	Got collective.xdv 1.0.
	Getting distribution for 'dv.xdvserver'.
	Got dv.xdvserver 1.0b5.
	Getting distribution for 'plone.postpublicationhook'.
	Got plone.postpublicationhook 1.0rc1.
	Getting distribution for 'plone.app.registry'.
	Got plone.app.registry 1.0a1.
	Getting distribution for 'plone.synchronize'.
	Got plone.synchronize 1.0b1.

If everything went according to plan, we now have collective.xdv installed. Time to start Plone and activate it for our site.
    
Usage
-----

The publication hook is installed automatically, but will not do anything
unless xdv is configured for a particular Plone site. To do that, first
install it in the quickinstaller as normal, and then go to the new "Theme
transform" control panel. Here, you can set the following options:

  Enabled yes/no
    Whether or not the transform is enabled.

  Domains
    A list of domains (including ports) that will be matched against
    the HOST header to determine if the theme should be applied. Note that
    127.0.0.1 is never styled, to ensure there's always a way back into Plone
    to change these very settings. However, 'localhost' should work just fine.
  
  Theme
    A file path or URL pointing to the theme file. This is just a
    static HTML file.

  Rules
    The filesystem path to the rules XML file.  
  
  Alternate themes
    A list of definitions of alternate themes and rules files for a different path.
    Should be of the form 'path|theme|rules' where path may use a regular expression 
    syntax, theme is a file path or URL to the theme template and
    rule is a file path to the rules file.
  
  Boilerplate
    XDV by default includes some 'boilerplate' XSLT that takes
    care of copying some basic header attributes. You can override the
    boilerplate XSL file by specifying a filename here.
    
  Absolute prefix
    If given, any relative URL in an ``<img />``, ``<link />``, ``<style />``
    or ``<script />`` in the theme HTML file will be prefixed by this URL
    snippet when the theme is compiled. This makes it easier to develop theme
    HTML/CSS on the file system using relative paths that still work on any
    URL on the server.
    
  Unstyled paths
    This is used to give a list of URL patterns (using regular
    expression syntax) for pages that will not be styled even if XDV is
    enabled. By default, this includes the 'emptypage' view that is necessary
    for the Kupu editor to work, and the manage_* pages that make up the
    ZMI.
    
Note that when Zope is in debug mode, the theme will be re-compiled on each
request. In non-debug mode, it is compiled once on startup, and then only
if the control panel values are changed.

Static files and CSS
--------------------

Typically, the theme will reference static resources such as images or
stylesheets. It is usually a good idea to keep all of these in a single,
top-level directory to minimise the risk of clashes with Plone content paths.

If you are using Zope/Plone standalone, you will need to make your static
resources available through Zope, or serve them from a separate (sub-)domain.
The easiest way to do this is via a Plone folder with files, but a skin layer
directory view in portal_skins may also work.

If you have put Apache, nginx or IIS in front of Zope, you may want to serve
the static resources from the web server directly.

Controlling Plone's default CSS
-------------------------------

It is sometimes useful to show some of Plone's CSS in the styled site. You
can achieve this by using an xdv ``<append />`` rule or similar to copy the
CSS from Plone's generated ``<head />`` into the theme. You can use the
portal_css tool to turn off the style sheets you do not want.

However, if you also want the site to be usable in non-themed mode (e.g. on
a separate URL), you may want to have a larger set of styles enabled when
xdv is not used. To make this easier, you can use the following expressions
as conditions in portal_css (and portal_javascripts, portal_kss,
portal_actions, in page templates, and other places that use TAL expression
syntax):

  portal/@@xdv-check/enabled 
    Will return True if xdv is currently
    enabled. This will check both the 'enabled' flag in the Theme Transform 
    settings, and the current domain. Use 'not: portal/@@xdv-check/enabled' 
    to 'hide' a style sheet from the themed site.
    
  portal/@@xdv-check/domain_enabled
    Similar to the 'enabled' check, but
    only checks the domain, not the global 'enabled' flag in the control
    panel. This is useful if you want to apply the xdv transform outside
    Plone, but still need a way to control which domains get which styles.

Interaction with CacheFu
-------------------------

If you are using collective.xdv with Plone's CacheFu system, you will need
to disable GZIP compression in CacheFu's control panel. You may use
compression in e.g. Apache or nginx in front of Zope, but you can't apply
the compression before the xdv transform.