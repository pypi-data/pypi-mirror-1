Introduction
============

This package provides an "error document" that can be used for 404 responses
and some middleware to trigger the correct responses.

It is useful if you are deploying a Plone site in a WSGI chain using
repoze.zope2. When an error (e.g. a 404 response is triggered) you can forward
to a page in Plone, which can display suggestions and a friendly error message.

Furthermore, if an alias can be found in the redirection storage from
plone.app.redirector, an automatic redirect will be issued, taking the user
to the new page.

Finally, there is a rudimentary UI to bulk load redirects. This is useful if
you are migrating from an old site (perhaps not even a Plone site). Go to
http://localhost:8080/your-site/@@bulk-load-aliases as a Manager user,
and paste in the old and new paths in the form::

    /index.php?pageId=123  =>  /some-page/some-where
    
Note: The portal root path will be automatically prefixed to the paths.
Thus, the example above run on the Plone site 'mysite' would result in
an underlying redirect of /mysite/index.php?pageId=123 to
/mysite/some-page/some-where. The assumption is that you'll deploy with
virtual hosting so that the 'mysite' is the VHM root and not shown as
part of the URL, but part of rewrite rules.
 
To remove aliases, install Products.RedirectionTool and use its UI. 

Installation
------------

collective.fourohfour uses plone.app.registry and z3c.form.

To use the product in your own build, either depend on it in a setup.py file,
or add it to your buildout's `eggs` listing as normal.

In either case, you probably want to use a Known Good Set of packages to
minimise the risk of package version conflicts. For example::

  [buildout]
  ...
  extends =
      ...
      http://good-py.appspot.com/release/plone.autoform/1.0b2

  ...
  
  [instance]
  eggs =
      Plone
      collective.fourohfour
      ...

Once configured in your build, install the package from portal_quickinstaller
as normal. 

Hint: You may also want to install Products.RedirectionTool to get some GUI
support for modifying aliases.

Configuration
-------------

The middleware must be configured to be run before Paste#httpexceptions. For
example::

    [filter:errorhandler]
    use = egg:collective.fourohfour#handler
    404 = /@@404-error
    
    [filter:errorlog]
    use = egg:repoze.errorlog#errorlog
    path = /__error_log__
    keep = 50
    ignore = 
        paste.httpexceptions:HTTPUnauthorized
        paste.httpexceptions:HTTPNotFound
        paste.httpexceptions:HTTPFound
    
    [app:zope2]
    paste.app_factory = repoze.obob.publisher:make_obob
    repoze.obob.get_root = repoze.zope2.z2bob:get_root
    repoze.obob.initializer = repoze.zope2.z2bob:initialize
    repoze.obob.helper_factory = repoze.zope2.z2bob:Zope2ObobHelper
    zope.conf = /path/to/etc/zope.conf
    
    [pipeline:main]
    pipeline =
        errorhandler
        egg:Paste#httpexceptions
        egg:repoze.retry#retry
        egg:repoze.tm#tm
        egg:repoze.vhm#vhm_xheaders
        errorlog
        zope2

Please note::

  * The errorhandler middleware must be configured with a set of response
    types and the error page to redirect to. To use the "smart" view
    provided by this package, use /@@404-error.
    
  * If you use repoze.vhm for virtual hosting, the view path will be
    adjusted for the VHM root. Thus, in a typical setup where you virtual-
    host the Plone site at the root of the domain, a path of /@@404-error
    will do the right thing. However, if virtual hosting is not enabled,
    you'll need to adjust the path in the configuration file to include
    your Plone site, e.g. /my-site/@@404-error
  
  * The errorhandler middleware should come just before Paste#httpexceptions

It is possible to handle other types of responses with the same middleware,
e.g.::

     [filter:errorhandler]
     use = egg:collective.fourohfour#handler
     404 = /@@404-error
     500 = /default_error_message
 
 (This middleware is based on Paste#errordocument, but allows more of the
 original request to be passed through to the error handler, and also allows
 the error handler to raise 301/302 redirects).
  