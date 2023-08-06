This is a web gateway for IMDbPY (http://imdbpy.sourceforge.net).

INSTALLING
----------

Other than IMDbPY, the only requirement for IMDbPYKit is Paste Webkit
(http://pythonpaste.org/webkit/). The easiest way to install everything
is using easy_install:

easy_install imdbpykit

RUNNING
-------

You will need a web server to host the application. Since IMDbPYKit is a
WSGI application, any compliant server should work. Sample configuration files
have been provided for several servers, the necessary steps for using them have
been explained below. Remember to remove the ".sample" extension when copying
the sample files to their final locations. (Note: The location of the installed
files depends on your installation. For easy_install, they will be under the
directory created for the imdbpykit egg in site-packages.)

WSGIUtils (http://pypi.python.org/pypi/WSGIUtils/)
  You can install this package via easy_install.
  Copy the sample file for imdbpykit.ini to any directory, comment out
  the section:main part for the Paste Script server and run the command:
    paster serve imdbpykit.ini

Spawning (http://pypi.python.org/pypi/Spawning/)
  You can install this package via easy_install.
  Copy the sample file for imdbpykit.ini to any directory, comment out
  the section:main part for the Spawning server and run the command:
    spawn --factory=spawning.paste_factory.config_factory imdbpykit.ini

Apache with mod_wsgi
  Copy the sample files for imdbpykit.ini and imdbpy.wsgi to any directory.
  Copy the sample file for wsgi.conf to the Apache configuration directory
  and edit the paths for the imdbpy.wsgi script and the static files.

Don't forget to make sure that the web server has write permissions on the cache
directory (under web/static).

By default, IMDbPYKit will serve pages as XML along with an XSL stylesheet. This
will require an XSL-capable browser on the client side. It is tested with the
Firefox browser (http://www.mozilla.org/). If you would like to
serve pages as HTML, you have to install lxml (http://codespeak.net/lxml/)
and set the output mode in the config file to 'html'.

NEW STYLES
----------

If you would like to use your own stylesheet, create a new XSL file, put it in
the static files directory and set the 'style' option in the configuration file.
For example, if your style file is named 'monty.xsl', place it as:
  imdbpykit -> web -> static -> monty.xsl
and enter the following line in the 'app:main' section of the ini file:
  style = monty

TRANSLATIONS
------------

There is preliminary support for different languages using the gettext
translation system. To activate it, set the 'i18n' option to 'on' in the
configuration file and set the LANG environment variable when running the
server, like (for Unix):
  LANG=tr_TR paster serve imdbpykit.ini

The tag names in the IMDbPY XML serve as the message ids. You can find a simple
example for English in the locale directory. If you want to translate to another
language, simply create a new file as 'imdbpykit-xx.po' in the locale directory,
where 'xx' is the code for the new language. IMDbPYKit will compile and use
these message catalogs automatically on startup.
