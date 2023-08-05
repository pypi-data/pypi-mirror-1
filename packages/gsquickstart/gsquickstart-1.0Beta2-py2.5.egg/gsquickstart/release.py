# Release information about gsquickstart

version = "1.0Beta2"

description = "TurboGears genshi quickstart template"
long_description = """

gsquickstart is a Turbogears template plugin for genshi template.
It will install a paste template for Turbogears' quickstart usage.

Install
-----------
Install with setuptools::

    $easy_install gsquickstart

Usage
-----------

gsquickstart Just as normal tg-admin quickstart, 
but you've to specify the tggenshi(TurboGears Genshi) template instead of the default kid template::

    $tg-admin quickstart -t tggenshi [project name]


Notice
---------

TurboGears 1.0 documents are written for the default setting of kid+sqlobject.

But genshi template has some difference between kid template. 

You may expect problems when using genshi template instead.

Take widgets for example, you've to use '${ET(myform())}' instead of '${myform()}' in template.


What's new in Beta2?

* Able to be indexed by turbogears cogbin 

""" 
author = "Fred Lin"
email = "gasolin+tg@gmail.com"
copyright = "Fred Lin 2007"

# if it's open source, you might want to specify these
url = "http://trac.turbogears.org/browser/projects/GenshiQuickStart"
download_url = "http://www.python.org/pypi/gsquickstart/"
license = "MIT"
