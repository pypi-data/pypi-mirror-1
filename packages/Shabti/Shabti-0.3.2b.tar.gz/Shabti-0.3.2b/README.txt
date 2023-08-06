.. _shabti: Shabti

======
Shabti
======

Shabti is a fork of Tesla with the code brought up to date with respect to Pylons 0.9.7, SQLAlchemy 0.5 and Elixir 0.7. The change of name reflects a different orientation, the main goal of Shabti now is to provide some quick and easy kickstarts for building web applications in Pylons.

About Shabti
============

Shabti is a number of different sets of Pylons project templates, each of which augments the standard Pylons "scaffolding" with selective additional resources, such as the integration of Elixir, a declarative layer on top of SQLAlchemy. Shabti adds extra project-handling commands to paster and makes the augmented Pylons templates available to the standard Pylons project creation command: 

$ paster create --template <shabti_template_name> <project_name>Shabti is named after the ancient Egyptian funerary figurines that "were placed in tombs among the grave goods and were intended to act as substitutes for the deceased, should he be called upon to do manual labor in the afterlife." --- wikipedia

Shabti is a fork of Tesla with the code brought up to date with respect to Pylons 0.9.7, SQLAlchemy 0.5 and Elixir 0.7.

The change of name reflects a different orientation, the main goal of Shabti now is to provide some quick and easy kickstarts for building web applications in Pylons. 

Shabti is open source and is maintained in a Bitbucket project.

This document is pertinent to Shabti version 0.3.0 and is adapted from the original introduction to Tesla.

Introduction
============

Shabti is just a thin layer of glue around several related Python libraries, namely:

Pylons :: web framework

SQLAlchemy :: ORM and SQL generation

Elixir :: declarative layer for SQLAlchemy

Paste :: WSGI server and other tools

FormEncode :: form validation

Toscawidgets :: form widgets middleware

rdflib :: RDF and SPARQL

RDFAlchemy :: Object-RDF Mapper

In addition to these core libraries Shabti makes optional use of the sqlalchemy-migrate library for handling database migrations with SQLAlchemy.

It is strongly recommended that developers at least familiarize themselves with the documentation of these core libraries first.

Philosophy and design goals
===========================

Shabti is a re-working of Tesla, which started as a simple template with glue code for Pylons and SQLAlchemy plus Elixir so that developers could get started quickly with these libraries. Some additional paster command line tools were added for common handlng database management tasks, inspired by similar tools available to developers working with Rails and Django.

The AuthKit library was initially widely used by Pylons developers for handling authentication and authorization work. In consequence, an additional Shabti template, shabti_auth, implemented AuthKit integration and provided a set of very basic classes for User, Group and Permission entities. However, the previous author decided to remove the AuthKit dependency due to various design and documentation issues with that library.

Shabti extends the notion beyond ORM support for relational store into support for i) hierarchical store via the eXist native XML database's XMLRPC controller and ii) directed graph store via rdflib and RDFAlchemy. 

Getting started
===============

Shabti cannot yet be installed from the Cheeseshop using setuptools (this is likely to change at some future point). In the interim, the latest development version can be downloaded from the Mercurial repository listed on the Shabti Bitbucket project page.

$ hg clone http://bitbucket.org/gjhiggins/shabti/ followed by

$ python setup.py developCreating an application using Shabti templates
==============================================

As with Pylons, a new skeleton application is created by using paster:

$ paster create -t <template_name> <project-name>The command paster create --list-templates will show a list of available application templates. The Shabti templates are:

shabti :: default Shabti project template, provides Pylons and Elixir on top of SQLAlchemy

shabti_auth :: creates additional code for handling authentication

shabti_auth_xp :: as shabti_auth but with row-level permissions (experimental)

shabti_rdfalchemy :: provides RDFAlchemy ORM - Object-RDF Mapper

shabti_microsite :: auth'n'auth, tw.forms, a micro-CMS and a fluid vari-column layout

The shabti_auth_xp template is experimental. This will be merged with shabti_auth at some point in the future (probably in version 0.4). The shabti_auth template features are explained in further detail below.

Commands added to Paster
========================

Shabti uses the paster command line tool that comes with Paste. Most of the common paster commands are explained in the Pylons documentation. Shabti adds some extra commands of its own, mainly for database management:

$ paster model <model_name> [--no-test]Creates a skeleton Python module, <model_name>.py, in the model directory of your Shabti application. In addition, a corresponding skeleton unit test module, test<model_name>.py, is added to the tests/unit directory of your Shabti package, along with a directory for storing your test fixtures and other fixtures. If the --no-test flag is passed then the test files are not created.

$ paster create_sql [--table=table] [--setup] config-fileCreates all tables (i.e. CREATE TABLE) based on available model classes. The config-file argument is always required, e.g. development.ini. You must provide the correct URI to your database in the configuration setting sqlalchemy.default.uri (see (LINK) for the correct URI for your database vendor). 

Note that for a model class to be "visible" to the database commands, it has to be imported in the __init__.py file of the project's model package. An example:

from mymodel import MyModelOptionally, the name of a single table can be passed to create_sql with the --table argument. Adding the --setup flag will run setup-app (i.e. the websetup.py file of the application) after the tables have been created.

$ paster drop_sql [--table=table] config-fileDrops all available tables (i.e. DROP TABLE), or a single named table if given in the --table argument.

$ paster reset_sql [--table=table] [--setup] config-fileDrops all available classes and then re-creates them (or single table given in --table argument). As with create_sql, including the --setup flag causes websetup.py to be executed.

$ paster runner --create <script_name>Creates a skeleton Python script, <script_name>.py, in the scripts directory of the Shabti application package. This script is used for running background tasks outside the web application, with cron for example.

$ paster runner <script-name> config-fileRuns a script that was created with runner --create. This command can be used with cron for running repetitive or timed tasks. A config-file argument (e.g. development.ini) is mandatory.

Migrations package
==================

Shabti uses the sqlalchemy-migrate utility for running database migrations with SQLAlchemy. Shabti integrates a number of migration tasks with paster. See the migrate documentation and source code for an explanation of these commands; they are just summarized below for convenience.

$ paster migrate config-file migration-command 
    [--dburi=uri] [--repository=repo_dir] [--version=version] 
    [--version_table=version_table] [--preview_py] [--preview_sql]The config-file argument is the name of the configuration file (e.g. development.ini). The migration-command argument may be one of the following:

commit

test

version

db_version

source

upgrade

downgrade

drop_version_control

A note about the template engine
================================

Shabti uses the Mako templating engine by default, which is the default template engine used by Pylons. Mako is very fast and flexible. However, if another template engine is preferred, such as Genshi (not longer such a good example as it is now supported as an alternate default for Pylons but Evoque and Brevé are other examples), it is trivial to set up another template engine for use with Pylons. Developers should consult the Pylons documentation for the full details of the dozen or sol lines of code required.

The Shabti Templates
====================

The templates listed here are complete and working but deserve more sophisticated tests. 

shabti :: Pylons with Elixir on SQLAlchemy
==========================================

The default shabti template integrates Elixir into Pylons for those developers who wish to use a high-level declarative layer on top of SQLAlchemy, after the "Active Record" design pattern.

At one point Elixir was under consideration as an supported component of Pylons but this intention had to be abandoned as people persistently failed to understand that developing with high-level abstractions is not as simple as it might appear at first glance.

Developers are cautioned that a significant degree of familarity with SQLAlchemy is a prerequisite for using Elixir.

For those developers who are interested in more details, see the associated practical notes on using Elixir with Pylons and other Elixir topics including the generation of Elixir models from UML diagrams produced in ArgoUML.

shabti_auth :: boilerplate authentication
=========================================

The shabti_auth template includes the additions from the default shabti template (i.e. Elixir on SQLAlchemy) and add boilerplate authentication code as a basic design pattern to help developers get started. This includes:

controller-level permission-handling

action-level permission handling (decorators)

authentication helpers

basic identity classes (User, Group and Permission)

The idea behind the shabti_auth template is to do the 80% hard/repetitive work that characterises most auth'n'auth requirements and to be stay out of the developer's way during the more intensive development of the last 20% of the task.

For example, the User class only has the bare minimum of fields such as username and password. It is the responsibility of the developer to add additional fields according to the domain requirements (e.g. address fields or phone number). In addition, the default password encryption (using SHA1) may not be stringent enough certain security requirements; if this is the case, then the template-generated code must then be rewritten in order to satisfy more stringent needs.

The template creates a set of permission classes (located in lib/permissions.py in the Shabti application package) which can be used at the controller or action level, or as helpers in templates. These classes can be easily extended or custom alternatives can be created. In addition there are three Elixir identity classes (User, Group and Permission) which store the relevant authentication and authorization information to the database. They are located in lib/model/identity.py. The @authorize decorator, located in lib/decorators.py, can be used in conjunction with the permission classes. See the source code for more information on using this decorator.

The shabti_auth_xp template includes code for row-level permissions. This allows the developer to set permissions on individual instances rather than just system-wide permissions. For example, a NewsItem class might have "edit" and "delete" permissions set for each NewsItem instance. The permissions system is implemented as an Elixir Statement, has_permissions. The relevant code is located in model/permissions.py in the Shabti application package. One feature of this system is that permission checking can be overriden, for example granting default "edit" permission to the author of a NewsItem. This makes it quite flexible in more complex situations.

In addition the shabti_auth_xp template provides a sub-class of BaseController, ModelController. The ModelController instance will automatically lookup an instance of the given model class if the "id" parameter is passed in the URL, also handling permission checks if needed. 

The shabti_auth_xp template is experimental (i.e. for study purposes only) and will be merged with the shabti_auth and default shabti templates in future versions.

shabti_rdfalchemy :: an Object-RDF Mapper
=========================================

The goal of RDFAlchemy is to provide Python users with an object-type API access to an RDF triple store. In the same way that SQLAlchemy is an ORM (Object Relational Mapper) for relational database users, RDFAlchemy is an ORM (Object RDF Mapper) for RDF triple store users.

RDFAlchemy supports several different methods of connecting to triple stores (either as the exclusive persistence mechanism or in parallel with SQLAlchemy connections to conventional relational tables).

RDFAlchemy supports D2Rq access to relational tables, SPARQL access via Joseki to triples store maintained by either Jena or Sesame, REST access to Sesame-maintained triple stores and direct library access to rdflib-maintained triple stores (optionally either rdflib-specific or via the rdflib-Redland bridge).

(Temporary Filler, ground under repair ...) 

Presumably, an important property of these three types of EC is to be regarded as nondistinctness in the sense of distinctive feature theory.

This suggests that any associated supporting element suffices to account for the ultimate standard that determines the accuracy of any proposed grammar. Suppose, for instance, that the systematic use of complex symbols is, apparently, determined by the extended c-command discussed in connection with (34).

(End of filler)

The use of persistent objects in RDFAlchemy will be as close as possible to what it would be in SQLAlchemy. The aim is be able to write code such as:

>>> c = Company.get_by(symbol = 'IBM')
>>> print c.companyName
International Business Machines Corp.technical notes
===============

As the below overview diagram suggests, the shabti_rdfalchemy template requires certain dependencies to be satisfied. In a similar way that SQLAlchemy relies on psycopg2 to be able to connect to PostgreSQL, RDFAlchemy relies on the rdflib RDF library to be able to connect to triple stores.

Satisfying the rdflib dependency can present problems. The recommended approach is to follow the rdflib web site's explicit easy_install instructions, either 

$ easy_install -U rdflib==devor

$ easy_install -U "rdflib>=2.4,<=3.0a"The bottom line of the overview diagram shows that choice of back-end storage is constrained by support limitations. When using rdflib to maintain triple stores, SQLite is the minimal functional requirement for persistence, however performance is likely to become an early issue because the triple stores tend to expand alarmingly quickly and performance is critically dependent on fast indexing. 

From a practical perspective, MySQL is well-supported, ZODB and Sleepycat have proved to be unexpectedly quick (perhaps unhindered by RDBMS management processing), PostgreSQL (untuned) is disappointingly slow. Neither Jena nor Sesame stores are directly accessible from Pylons but both offer REST access.

Some additional practical notes of using RDFAlchemy with Pylons are available.

shabti_microsite :: a kick-the-tyres microsite
==============================================

The shabti_microsite template generates a very small populated web site with an identity model driving the auth'n'auth, complete with an "admin" login (generated by the contents of websetup.py and running "paster setup-app development.ini"), a basic page content model driving a forms-based micro-CMS dashboard.

Unlike the standard default Pylons project template, the model, controllers and view components are populated, providing a very rough-and-ready design pattern. 

The site includes examples of forms and validators and provides an integrated set of Genshi and Mako templates implementing a fluid, table-less 1, 2 or 3-column layout solution with a standard framework of CSS stylesheets.

Some effort has been devoted to modularising the templates according to broad function (for example there is a component that advertises a standard range of GRDDL transformations).

The code is simple and makes a very direct expression of some simple idioms in order to act as a quick sketch of the basic principles.

It may possibly have some use as a starting point from which to develop something more contextually specific, for example a customised, in-house proto-framework because the micro-site and the Shabti code together provide a worked example of how to create Paste templates and add commands to paster. 

The micro-site also offers a worked example of tw.forms, a web forms package based on the Toscawidgets middleware widget rendering and input validation package.

A set of the current Pylons official documents is included in Sphinx-rendered "web" format (fpickle) along with a "docs" controller providing a standalone docs browser.

NB: there are several dependencies: the micro-site is complete with a log4j.xml file and is configured to send logging to Apache chainsaw, so XMLLayout is required (unless the chainsaw logging configuration is commented out and the standard, commented-out logging configuration is uncommented.) Other dependencies are: Toscawidgets, tw.forms and Babel.

The following images give some idea of the appearance of the micro-CMS. 

Login panel and admin dashboard, showing changelog.

Page editing subsection, page editing form.

Rendered page, included Pylons docs and docs controller.

Note, the micro-site styling has yet to be ported to Shabti livery.

Reporting bugs and asking questions
===================================

If bugs or other issues with Shabti are encountered, they may be reported at the Bitbucket project page (http://www.bitbucket.org/gjhiggins/shabti/issues/). However, please ensure that the issue lies with Shabti and not with one of the libraries it uses such as Elixir, SQLAlchemy or Pylons. In that case, it is more appropriate to report the bug at the relevant discussion group where it is far more likely to get fixed.

With respect to questions or suggestions regarding Shabti, probably the best place to ask is the Pylons Google discussion group (http://groups.google.com/group/pylons-discuss) or the Pylons IRC channel (#pylons).

Credits
=======

The original Tesla code was written by Dan Jacob and Ben Bangert. My contribution doesn't extend beyond a bit of editing and some copying'n'pasting.

Images are courtesy of wikipedia.org.

