from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(
    name="Pylons",
    version="0.8",
    description='Pylons Web Framework',
    long_description="""
The Pylons web framework is aimed at making webapps and large programmatic website
development in Python easy. Several key points:

* A framework to make writing web applications in Python easy

* Inspired by Rails and TurboGears

* Utilizes a minimalist, component-based philosophy that makes it easy to expand on

* Built mainly as a customization of Myghty with Routes and Paste integration

* Harness existing knowledge about Python

Knowing Python makes Pylons easy
---------------------------------

Pylons makes it easy to expand on your knowledge of Python to master Pylons for web
development. Using a MVC style dispath, Python knowledge is used at various levels:

* The Controller is just a basic Python class, called for each request. Customizing the
  response is as easy as overriding __call__ to make your webapp work how you want.

* Myghty templating compiles directly to Python byte-code for speed and utilizes Python
  for template control rather than creating its own template syntax for "for, while, etc"

Current Status
---------------

Pylons is currently quite stable (built mostly with the mature Myghty package), and is
being used in production environments. Dependant packages are automatically installed 
from the following URL:

* `Dependant Packages svn <http://www.pylonshq.com/download/>`_

""",
    author='Ben Bangert, James Gardner',
    author_email='ben@groovie.org',
    url='http://pylons.groovie.org/',
    packages=find_packages(exclude=['ez_setup']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "Routes>=1.3", "Myghty>=1.0.1", "Paste>=0.5, <0.6",
        "PasteDeploy>=0.5, <0.6","PasteScript>=0.5, <0.6",
        "simplejson==1.1", "WSGIUtils==0.7", "WebHelpers>=0.1",
        "nose>=0.8.7",
        ],
    classifiers=["Development Status :: 4 - Beta",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: BSD License",
                 "Programming Language :: Python",
                 "Topic :: Internet :: WWW/HTTP",
                 "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
                 "Topic :: Software Development :: Libraries :: Python Modules",
               ],
    extras_require = {
        'pudge': ["docutils>=0.4", "elementtree>=1.2.6", "kid>=0.9",  "pudge==dev,>=0.1.1dev", "buildutils==dev,>=0.1.2dev",],
        'test': ["py>=0.8.0_alpha2"],
        'cheetah':["Cheetah>=1.0", "TurboCheetah>=0.9.5"],
        'kid':["kid>=0.9", "TurboKid==dev,>=0.9.1dev"],
    },
    entry_points="""
    [paste.paster_command]
    controller=pylons.commands:ControllerCommand
    compile_templates=pylons.commands:CompileCommand

    [paste.paster_create_template]
    pylons=pylons.util:PylonsTemplate
    
    [distutils.commands]
    lang_extract = pylons.i18n:LangExtract
    lang_compile = pylons.i18n:LangCompile
    """,
)