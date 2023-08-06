from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

version = '0.3.1'

setup(
    name= 'Shabti',
    version=version,
    author="Graham Higgins",
    author_email="gjh@bel-epa.com",
    keywords='web wsgi framework sqlalchemy elixir pylons paste template',
    description='Pylons template with Elixir ORM bindings',
    long_description="""
Shabti
======

Shabti is a set of Pylons kick-start services built on Pylons/Paste and, variously Elixir, SQLAlchemy, rdflib, RDFAlchemy. It includes paster commands for database management, migrations and model scaffolding, plus AuthKit integration. With just a little bit of glue Shabti gives you a major kick-start using the best Python web development libraries around today.

Current Status
---------------

Shabti %s described on this page is stable.

There is also an unstable `development version
<http://www.bitbucket.org/gjhiggins/shabti/overview/>`_ of Shabti.

Download and Installation
-------------------------

Shabti can be installed with `Easy Install
<http://peak.telecommunity.com/DevCenter/EasyInstall>`_ by typing::

 > easy_install Shabti


More information
----------------

Check out the project home pages on `BitBucket <http://www.bitbucket.org/gjhiggins/shabti/overview/>`_
and `Bel-EPA <http://bel-epa.com/shabtidocs/>`_

""" % version,
    license='MIT License',
    url='http://www.bitbucket.org/gjhiggins/shabti',
    dependency_links=[
        "http://www.bitbucket.org/gjhiggins/shabti/overview/"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Pylons",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False,
    packages=find_packages(),
    install_requires=["Pylons>=0.9.7", 
                      "simplejson>=1.7.1",
                      "Elixir>=0.6.1",
                      "SQLAlchemy>=0.5.1",
                      'sqlalchemy_elixir_validations'],
    extras_require={"migrate" : ["sqlalchemy-migrate>=0.4.6.dev-r445"],
                    "shabti_rdfalchemy" : ["RDFAlchemy==0.2b2dev-r106","rdflib>=2.4.0"],
                    "shabti_auth_couchdb" : ["CouchDB>=0.4"],
                    "shabti_authkit" : ["authkit>=0.4.2"],
                    "shabti_auth_repoze" : ["repoze.who>=1.0.1"],
                    "shabti_microsite" : ["Babel>=1.0.1","ToscaWidgets>=0.9.4dev-20080824", "tw.forms>=0.9.3dev-20090122"]
                    },
    include_package_data=True,
    entry_points="""
        [paste.paster_command]
        runner = shabti.commands:RunnerCommand
        migrate = shabti.commands:MigrateCommand
        model = shabti.commands:ModelCommand
        create_sql = shabti.commands:CreateSqlCommand
        drop_sql = shabti.commands:DropSqlCommand
        reset_sql = shabti.commands:ResetSqlCommand
        scaffold = shabti.commands:ScaffoldCommand
        [paste.paster_create_template]
        shabti = shabti.template:ShabtiTemplate
        shabti_auth = shabti.template:ShabtiAuthTemplate
        shabti_auth_xp = shabti.template:ShabtiAuthXpTemplate
        shabti_auth_couchdb = shabti.template:ShabtiAuthCouchdbTemplate
        shabti_auth_repozewho = shabti.template:ShabtiAuthRepozeWhoTemplate
        shabti_auth_repozewhat = shabti.template:ShabtiAuthRepozeWhatTemplate
        shabti_auth_repozepylons = shabti.template:ShabtiAuthRepozePylonsTemplate
        shabti_auth_rdfalchemy = shabti.template:ShabtiAuthRDFAlchemyTemplate
        shabti_authkit = shabti.template:ShabtiAuthkitTemplate
        shabti_blog = shabti.template:ShabtiBlogTemplate
        shabti_microsite = shabti.template:ShabtiMicroSiteTemplate
        shabti_quickwiki = shabti.template:ShabtiQuickWikiTemplate
        shabti_rdfalchemy = shabti.template:ShabtiRDFAlchemyTemplate
    """)

