#!/usr/bin/env python

# This is the ScanBooker Python package setup script.

import os
import sys

from setuptools import setup, find_packages
from setuptools.command import sdist
del sdist.finders[:]

sys.path.append('./src')
from scanbooker import __version__

basePath = os.path.abspath(os.path.dirname(sys.argv[0]))

scripts = [ 
    os.path.join('bin', 'scanbooker-makeconfig'),
    os.path.join('bin', 'scanbooker-admin'),
    os.path.join('bin', 'scanbooker-test'),
]

setup(
    name='scanbooker',
    version=__version__,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    scripts=scripts,
    include_package_data = True,
    package_data = {
        'scanbooker.django.templates.registry': ['*.html'],
    },
    zip_safe = False,
    install_requires = [
        'domainmodel==0.8',
    ],
    author='Appropriate Software Foundation',
    author_email='scanbooker-dev@appropriatesoftware.net',
    license='GPL',
    url='http://appropriatesoftware.net/scanbooker/Home.html',
    #download_url='http://appropriatesoftware.net/provide/docs/scanbooker-%s.tar.gz' % __version__,
    description='The ScanBooker system is a domainmodel application which supports medical imaging administration.',
    long_description =\
"""
ScanBooker is a domainmodel application, designed to support medical imaging administration. ScanBooker has a rich model of the medical imaging domain, which provides for tracking organisations, groups, researchers, training level, projects, ethics approvals, cost accounting, volunteers, and more. ScanBooker also provides a calendar for scheduling sessions with close reference to the model. ScanBooker was originally developed in a collaboration between the UK's Medical Research Council and the Appropriate Software Foundation. ScanBooker is stable, under active development, and upgrades are released with a tested data migration path.
""",
#    data_files=[
#        ('etc', ['etc/scanbooker.conf.new']),
#        ('var/images', ['README.images']),
#        ('var/log', []),
#        ('var/www', [])
#        ] \
#        + getDataFiles('media', basePath, 'src/scanbooker/django/media') \
#        + getDataFiles('templates', basePath, 'src/scanbooker/django/templates/sui'),
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    zip_safe=False,
)

