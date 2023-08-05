import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
import re, os

version = '0.9.7'

news = os.path.join(os.path.dirname(__file__), 'docs', 'news.txt')
news = open(news).read()
parts = re.split(r'([0-9\.]+)\s*\n\r?-+\n\r?', news)
found_news = ''
for i in range(len(parts)-1):
    if parts[i] == version:
        found_news = parts[i+i]
        break
if not found_news:
    print 'Warning: no news for this version found'

long_description="""\
This is a pluggable command-line tool.

It includes some built-in features;

* Create file layouts for packages.  For instance, ``paste create
  --template=basic_package MyPackage`` will create a `setuptools
  <http://peak.telecommunity.com/DevCenter/setuptools>`_-ready
  file layout.

* Serving up web applications, with configuration based on
  `paste.deploy <http://pythonpaste.org/deploy/paste-deploy.html>`_.

The latest version is available in a `Subversion repository
<http://svn.pythonpaste.org/Paste/Script/trunk#egg=PasteScript-dev>`_.

For the latest changes see the `news file
<http://pythonpaste.org/script/news.html>`_.  This package requires
`Cheetah
<http://cheeseshop.python.org/packages/source/C/Cheetah/Cheetah-1.0.tar.gz>`_
"""

if found_news:
    title = 'Changes in %s' % version
    long_description += "\n%s\n%s\n" % (title, '-'*len(title))
    long_description += found_news

setup(
    name="PasteScript",
    version=version,
    description="A pluggable command-line frontend, including commands to setup package file layouts",
    long_description=long_description,
    classifiers=[
      "Development Status :: 4 - Beta",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: MIT License",
      "Programming Language :: Python",
      "Topic :: Internet :: WWW/HTTP",
      "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
      "Topic :: Software Development :: Libraries :: Python Modules",
      ],
    keywords='web wsgi setuptools framework command-line setup',
    author="Ian Bicking",
    author_email="ianb@colorstudy.com",
    url="http://pythonpaste.org/script/",
    namespace_packages=['paste'],
    license='MIT',
    packages=find_packages(exclude='tests'),
    package_data={
      'paste.script': ['templates/basic_package/setup.*',
                       'templates/basic_package/tests/*.py',
                       # @@: docs/ doesn't have any files :(
                       'templates/basic_package/+package+/*.py'],
      },
    zip_safe=False,
    scripts=['scripts/paster'],
    extras_require={
      'Templating': [],
      'Cheetah': ['Cheetah'],
      'Config': ['PasteDeploy'],
      'WSGIUtils': ['WSGIUtils'],
      'Flup': ['Flup'],
      # the Paste feature means the complete set of features;
      # (other features are truly optional)
      'Paste': ['PasteDeploy', 'Cheetah'],
      },
    entry_points="""
    [paste.global_paster_command]
    help=paste.script.help:HelpCommand
    create=paste.script.create_distro:CreateDistroCommand [Templating]
    serve=paste.script.serve:ServeCommand [Config]
    exe=paste.script.exe:ExeCommand
    points=paste.script.entrypoints:EntryPointCommand
    make-config=paste.script.appinstall:MakeConfigCommand
    setup-app=paste.script.appinstall:SetupCommand

    [paste.paster_command]
    grep = paste.script.grep:GrepCommand

    [paste.paster_create_template]
    basic_package=paste.script.templates:BasicPackage

    [paste.server_runner]
    wsgiutils=paste.script.wsgiutils_server:run_server [WSGIUtils]
    flup_ajp_thread=paste.script.flup_server:run_ajp_thread [Flup]
    flup_ajp_fork=paste.script.flup_server:run_ajp_fork [Flup]
    flup_fcgi_thread=paste.script.flup_server:run_fcgi_thread [Flup]
    flup_fcgi_fork=paste.script.flup_server:run_fcgi_fork [Flup]
    flup_scgi_thread=paste.script.flup_server:run_scgi_thread [Flup]
    flup_scgi_fork=paste.script.flup_server:run_scgi_fork [Flup]
    cgi=paste.script.cgi_server:paste_run_cgi

    [paste.app_factory]
    test=paste.script.testapp:TestApplication

    [paste.deployer]
    test=paste.script.testapp:Deployer

    [paste.entry_point_description]
    paste.entry_point_description = paste.script.entrypoints:MetaEntryPointDescription
    
    [console_scripts]
    paster=paste.script.command:run
    """,
    install_requires=[
      'Paste',
      'PasteDeploy',
      'Cheetah',
      ],
    )
