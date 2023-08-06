#!/usr/bin/env python
#
# Desire distutils setup.py
#
from distutils.core import setup
import sys
import os
import fnmatch
sys.path.append('./src')
from desire import __version__

basePath = os.path.abspath(os.path.dirname(sys.argv[0]))

# todo: package description.

def getDataFiles(dest, basePath, pathOffset, glob = '*.*'):
    """
    Get all files matching glob from under pathOffset put give their pathes
    relative to basePath
    """
    result = []
    pathToWalk = os.path.join(basePath, pathOffset)
    for root, dirs, files in os.walk(pathToWalk):
        if not '.svn' in root:
            toffset = root[len(basePath)+1:]
            toffsetForDest = root[len(pathToWalk)+1:]
            tfileNames = fnmatch.filter(files, glob)
            fileList = [os.path.join(toffset, fname) for fname in tfileNames]
            tdest = os.path.join(dest, toffsetForDest)
            result.append( (tdest, fileList) )
    return result

def getPackages(basePath):
    result = []
    for root, dirs, files in os.walk(basePath):
        if not '.svn' in root and '__init__.py' in files:
            toffset = root[len(basePath)+1:]
            result.append( toffset )
    return result

def getScripts(basePath, offset):
    """
    Assumes all scripts are in base directory
    """
    scriptsList = []
    scriptsDir = os.path.join(basePath, offset)
    for fileName in os.listdir(scriptsDir):
        if not ('.svn' in fileName or '.bak' in fileName):
            scriptsList.append(os.path.join(offset, fileName))
    return scriptsList

setup(
    name='desire',
    version=__version__,
    author='Appropriate Software Foundation',
    author_email='desire-dev@appropriatesoftware.net',
    license='GPL',
    url='http://appropriatesoftware.net/desire/Home.html',
    download_url='http://appropriatesoftware.net/provide/docs/desire-%s.tar.gz' % __version__,
    description='The desire system is a domainmodel application which supports analysis of event-driven story-based working processes and system supports.',
    long_description =\
"""
""",
    
    package_dir={'': 'src'},
    packages=getPackages(os.path.join(basePath, 'src')),
    
    scripts=[
        os.path.join(basePath, 'bin', 'desire-admin'),
        os.path.join(basePath, 'bin', 'desire-test'),
    ],
    data_files=[
        ('etc', ['etc/desire.conf.new']),
        ('var/images', ['README']),
        ('var/log', []),
        ('var/www', [])
        ] \
        + getDataFiles('var/www/media', basePath, 'src/desire/django/media') \
        + getDataFiles('var/django/templates', basePath, 'src/desire/django/templates'),
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


