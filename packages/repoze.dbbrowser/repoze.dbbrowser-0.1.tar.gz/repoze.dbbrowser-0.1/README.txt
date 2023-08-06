DB Browser
==========

This package provides a simple WSGI application to browse and edit
database tables. The application was developed using the repoze.bfg
web framework and uses the excellent JqueryUI library.

After installing and configuring the application, you will be able
to browse and edit your application's tables by visiting the
configured URL path. All the configuration that is needed is an
sqlalchemy database connection string for your database.

Installation
------------

Install using setuptools, e.g. (within a virtualenv)::

 $ easy_install repoze.dbbrowser

Configuration inside another repoze.bfg application
---------------------------------------------------

This package includes a repoze.bfg view callable, so that from another
repoze.bfg application, it is possible to configure it as a view. To do
so, simply add a view declaration inside your configure.zcml. Note
that your application's settings must include the sqlalchemy database
connection string for your database, under the name 'db_string'.

 <view
    view="repoze.dbbrowser.dbbrowser.app_view"
    name="dbbrowserapp"
    />

The result of the application call will be turned into a webob Response
and returned to repoze.bfg as if the application was a view.

Alternatively, this can be accomplished via Python when adding a view to
the repoze.bfg configurator:

 from repoze.dbbrowser.dbbrowser import app_view
 config.add_view(app_view, name='dbbrowserapp')

Configuration via Paste
-----------------------

The application can also be 'mounted' into another WSGI application
using Paste composite applications. Just choose a URL path for it and
add the corresponding section:

 [composite:main]
 use = egg:Paste#urlmap
 / = myapp
 /dbbrowser = dbbrowser

 [app:myapp]
 use = egg:myapp#app

 [app:dbbrowser]
 use = egg:repoze.dbbrowser#dbbrowser
 db_string = sqlite:///%(here)s/myapp.db
 theme_switcher = true
 default_theme = redmond

The only required parameter is 'db_string', which is an sqlalchemy
database connection string.

The 'theme_switcher' parameter is a boolean indicating if JQuery UI theme
switching functionality should be enabled.

The 'default_theme' parameter is a string giving the name of the JQuery UI
theme to be used for the default dbbrowser UI. Keep in mind that JQuery
stores this id in a cookie, so you may have to clear cookies for this setting
to take effect if a previous theme was selected with the switcher.

Reporting Bugs / Development Versions
-------------------------------------

Visit http://bugs.repoze.org to report bugs.  Visit
http://svn.repoze.org to download development or tagged versions.

