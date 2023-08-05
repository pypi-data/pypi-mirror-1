# Release information about gsquickstart

version = "1.0"

description = "TurboGears Genshi quickstart template"
long_description = """
gsquickstart is a TurboGears quickstart template plug-in for Genshi templates.
It will install a paste template which can be used with TurboGears' 
``tg-admin quickstart`` command.


Installation
------------

Installation with setuptools::

    $easy_install gsquickstart


Usage
-----

Creating a project
~~~~~~~~~~~~~~~~~~

The gsquickstart template is used like any other quickstart template with 
tg-admin quickstart, you just have to specify the template name, which is 
"tggenshi" (for TurboGears Genshi) with the ``-t`` option  template instead 
of the default kid template::

    $tg-admin quickstart -t tggenshi [project name]

This will install three basic Genshi tempaltes and set up the project 
configuration to use Gensi templates as default.


Updating a project
~~~~~~~~~~~~~~~~~~

For updating a project with the basic Genshi templates, change into your
project directory and run::

    tg-admin update -t tggenshi

Since the "turbogears" template already installs Kid templates in 
``<package>/templates``, they are removed by gsquickstart in a 
post-template-creation step. But when update your project dir, the Kid 
templates will be created again. Now gsquickstart can not just delete them 
again, because they might have been created earlier and on purpose by the 
developer.

What the new code does is: if it is an update command, prompt the user, 
if the files ``<package>/templates/{login,master,welcome}.kid`` should 
be removed (for each file). The default answer is 'n'. 


Notice
------

The TurboGears 1.0 documentation is written with the default setting of 
Kid & SQLObject in mind. The syntax of Genshi templates is very similar 
to that of Kid but there are some differences to bear in mind. 

For example, you need to make some changes to your templates, if you use 
widgets with Genshi templates: put ``${ET(myform())}`` instead of 
``${myform()}`` as a placeholder for widgets in the template.

You can find more information in the `TurboGears documentation`_ and on 
the `Genshi website`_.

.. _TurboGears documentation :http://docs.turbogears.org/1.0/GenshiTemplating
.. _Genshi website: http://genshi.edgewall.org/wiki/GenshiFaq


What's new?
-----------

1.0
---

* The quickstart template was stripped of almost all files shared with the
  standard "turbogears" template and now inherits from this template instead
  of from "tgbase". The only files that are added/overwritten by "tggenshi"
  are ``setup.py``, ``<package>/config/app.cfg`` and the Genshi templates
  in ``<package>/templates/*.html``. But see the "Updating a project" section
  above.
  
  The new template structure makes it easier to stay synchronized with changes
  to the standard turbogears template since most files will just be
  inherited from.

* Synchronized ``app.cfg_tmpl` and `setup.py_tmpl`` with the latest 
  "turbogears" template.


1.0Beta2
--------

* Able to be indexed by turbogears cogbin.
"""
author = "Fred Lin"
email = "gasolin+tg@gmail.com"
copyright = "Fred Lin 2007"

# if it's open source, you might want to specify these
url = "http://trac.turbogears.org/browser/projects/GenshiQuickStart"
download_url = "http://www.python.org/pypi/gsquickstart/"
license = "MIT"
