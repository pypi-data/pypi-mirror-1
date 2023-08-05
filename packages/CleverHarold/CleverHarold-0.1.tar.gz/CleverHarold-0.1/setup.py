#!/usr/bin/env python
from sys import version_info
from os.path import join

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
from pkg_resources import DistributionNotFound


if version_info < (2, 4):
    raise SystemExit('Clever Harold requires Python 2.4 or newer.')

description = open(join('docs', 'description.txt')).readlines()[2:]

setup(
    name='CleverHarold',
    version='0.1',
    author='Troy Melhase',
    author_email='troy@gci.net',
    download_url='http://www.cleverharold.org/releases/',
    license='GPL',
    description='Experimental Web Framework',
    url='http://www.cleverharold.org',

    packages=find_packages(),
    include_package_data=True,
    exclude_package_data={},
    extras_require={},
    zip_safe=False,
    test_suite='harold.tests.test_all.suite',
    
    long_description=str.join('', description),

    install_requires=[
        'cElementTree >= 1.0.2',
        'cheetah == 1.0',
        'docutils >= 0.4',
        'flup >= 0.5',
        'kid >= 0.9.3',
        'mechanize >= 0.1.2b',
        'Paste == 0.9.6',
        'PasteDeploy >= 0.9.6',
        'PasteScript >= 0.9.6',
        'simplejson >= 1.3',
        'SQLAlchemy >= 0.2.6',
        'static >= 0.3',
        'wsgiref > 0.1',
        ],

    entry_points="""
    [paste.global_paster_command]
    init-harold=harold.plugins.createproject:HaroldCreate
    
    [paste.paster_create_template]
    harold=harold.plugins.createproject:HaroldTemplate

    [paste.paster_command]
    recreate-models=harold.plugins.recreatemodel:RecreateModels
    show=harold.plugins.showproject:ShowProject
    shell=harold.plugins.modelshell:ModelShell
    harold=harold.plugins.serve:ServeHarold

    [paste.app_factory]
    static=harold.plugins.factory:wsgi_static_factory
    not_found=harold.plugins.factory:error_notfound

    [paste.filter_app_factory]
    debug_info=harold.plugins.factory:debug_info
    request_timer=harold.plugins.factory:request_timer

    cheetah_publisher=harold.plugins.factory:cheetah_publisher
    code_publisher=harold.plugins.factory:code_publisher
    kid_publisher=harold.plugins.factory:kid_publisher
    markdown_publisher=harold.plugins.factory:markdown_publisher
    rest_publisher=harold.plugins.factory:rest_publisher

    session=harold.plugins.factory:session_filter
    cache=harold.plugins.factory:cache_filter

    activemapper_provider=harold.plugins.factory:activemapper_provider
    dbapi_provider=harold.plugins.factory:dbapi_provider
    sqlalchemy_provider=harold.plugins.factory:sqlalchemy_provider
    sqlobject_provider=harold.plugins.factory:sqlobject_provider

    request_log=harold.plugins.factory:requestlog_writer
    """,

    platforms='POSIX',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',

        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',

        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )
    
