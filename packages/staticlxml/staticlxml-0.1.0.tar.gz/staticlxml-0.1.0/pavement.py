##############################################################################
#
# Copyright (c) 2008 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################
import os, shutil, sys, time

from paver.defaults import options, Bunch, task, sh, needs

__version__ = '0.1.0'

# please see repoze-license.txt


from setuptools import setup, find_packages

#here = os.path.abspath(os.path.dirname(__file__))
#README = open(os.path.join(here, 'README.txt')).read()
#CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
README= ''
CHANGES=''

install_requires=[]

options(
      setup =Bunch(name='staticlxml',
      version=__version__,
      description='A simple way to install lxml in a static manner',
      long_description="Right now this only works inside of a virtualenv",
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      keywords='',
      author="Christopher Perkins",
      author_email="chris@percious.com",
      url="http://www.percious.com",
      license="BSD",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires = install_requires,
      entry_points = """\
      """
      )
)

index = 'http://dist.repoze.org/lemonade/dev/simple'

#allow the index to be overridden by the -i flag
for i, arg in enumerate(sys.argv):
    if arg == '-i':
        index = sys.argv[i+1]

def create_fake_buildout():
    root = os.environ['VIRTUAL_ENV']
    fake_buildout = dict(buildout=dict(index=index))
    fake_buildout['buildout']['parts-directory'] = root
    fake_buildout['buildout']['directory'] = root
    return fake_buildout

@task
def checking_for_virtualenv():
    #see if we are in a virtualenv, and if we are not exit()
    try:
        os.environ['VIRTUAL_ENV']
    except KeyError:
        print 'this setup script cannot be run outside of a virtual environment.  Did you activate?'
        exit()

def get_site_packages_dir():
    root = os.environ['VIRTUAL_ENV']
    major_python_version = str(sys.version_info[0])
    minor_python_version = str(sys.version_info[1])
    python_version = major_python_version+'.'+minor_python_version
    return root+'/lib/python'+python_version+"/site-packages/"

import imp
from pkg_resources import fixup_namespace_packages, declare_namespace

def add_to_sys_path(package):
    site_packages_dir = get_site_packages_dir()
    for path in os.listdir(site_packages_dir):
        if path.startswith(package):
            sys.path.append(site_packages_dir+path)
            from pkg_resources import working_set
            working_set.add_entry(site_packages_dir+path)
            return

@task
@needs('checking_for_virtualenv')
def installing_zc_recipies():
    root = os.environ['VIRTUAL_ENV']

    try:
        import zc.buildout
    except ImportError:
        sh(root+'/bin/easy_install -i '+index+' zc.buildout')
        add_to_sys_path('zc.buildout')
        import zc.buildout


    try:
        import zc.recipe.egg
    except ImportError:
        sh(root+'/bin/easy_install -aZi '+index+' zc.recipe.egg')
        add_to_sys_path('zc.recipe.egg')
        import zc.recipe.egg

    try:
        import zc.recipe.cmmi
    except ImportError:
        sh(root+'/bin/easy_install -aZi '+index+' zc.recipe.cmmi')
        add_to_sys_path('zc.recipe.cmmi')
        import zc.recipe.cmmi

@task
@needs('installing_zc_recipies')
def installing_libxml2():
    fake_buildout = create_fake_buildout()
    name = ''
    url = 'http://dist.repoze.org/lemonade/dev/cmmi/libxml2-2.6.32.tar.gz'
    extra_options = '--without-python'
    options = dict(url=url, extra_options=extra_options)

    from zc.recipe.cmmi import Recipe
    recipe = Recipe(fake_buildout, name, options)
    recipe.install()

@task
@needs('installing_libxml2')
def installing_libslt():
    root = os.environ['VIRTUAL_ENV']
    fake_buildout = create_fake_buildout()
    name = ''
    url = "http://dist.repoze.org/lemonade/dev/cmmi/libxslt-1.1.24.tar.gz"
    extra_options = """--with-libxml-prefix="""+root+"""
--without-python"""
    options = dict(url=url, extra_options=extra_options)

    from zc.recipe.cmmi import Recipe
    recipe = Recipe(fake_buildout, name, options)
    recipe.install()

@task
@needs(['installing_libslt', 'installing_libxml2'])
def installing_lxml():
    root = os.environ['VIRTUAL_ENV']

    site_packages_dir = get_site_packages_dir()
    
    fake_buildout = create_fake_buildout()
    develop_eggs_dir = root+"""/develop-eggs/"""

    if not os.path.exists(develop_eggs_dir):
        os.makedirs(develop_eggs_dir)
    #install into site-packages
    fake_buildout['buildout']['develop-eggs-directory'] = develop_eggs_dir
    python = fake_buildout['buildout']['python'] = 'python'
    fake_buildout[python] = {}
    fake_buildout[python]['executable'] = root+"""/bin/python"""
    
    fake_buildout['buildout']['eggs-directory'] = develop_eggs_dir #site_packages_dir
    fake_buildout['buildout']['directory'] = root

    name = 'lxml'

    options = {}
    options['egg'] = 'lxml'
    options['include-dirs'] = root+"""/include/libxml2
"""+root+"""/include/"""
    options['library-dirs'] = root+'/lib/'
    options['rpath'] = root+'lib/'
    
    fake_buildout['lxml_environment'] = {'XSLT_CONFIG':root+'/bin/xslt-config',
                                         'XML2_CONFIG':root+'/bin/xml2-config'}
    options['environment'] = 'lxml_environment'
    
    from zc.recipe.egg import Custom
    recipe = Custom(fake_buildout, name, options)
    recipe.install()
    
    #copy the lxml egg to site-packages
    lxml_egg = os.listdir(develop_eggs_dir)[0]
    lxml_egg_path = develop_eggs_dir+'/'+lxml_egg
    if os.path.exists(site_packages_dir+'/'+lxml_egg):
        shutil.rmtree(site_packages_dir+'/'+lxml_egg)
    shutil.copytree(lxml_egg_path, site_packages_dir+'/'+lxml_egg)
    
    #and write a path file into site-packages
    lxml_file = file(site_packages_dir+'/'+lxml_egg+'.pth', "w")
    lxml_file.write(site_packages_dir+'/'+lxml_egg)
    lxml_file.close()
    
@task
@needs('installing_lxml')
def install():
    call_task("setuptools.command.install")
    
@task
@needs(['generate_setup', 'minilib', 'setuptools.command.sdist'])
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass
