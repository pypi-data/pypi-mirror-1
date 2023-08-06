try:
    from paver.virtual import bootstrap
except :
    # minilib does not support bootstrap
    pass

from paver.defaults import task, options, Bunch
from paver.defaults import cmdopts 
from paver.runtime import call_task 
from setuptools import find_packages

version = '0.1b'

description = ''.join([x for x in open('README.txt')])

jstools_bunch = Bunch(
    name='JSTools',
    version=version,
    description="assorted python tools for building (packing, aggregating) javascript libraries",
    long_description=description,
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='javascript',
    author='assorted',
    author_email='info@opengeo.org',
    url='http://projects.opengeo.org/jstools',
    license='various / BSDish',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=["decorator",
                      "plone.memoize"],
    entry_points="""
    [zc.buildout]
    default=jstools.bo:BuildJS
    buildjs=jstools.bo:BuildJS
    [console_scripts]
    jsbuild=jstools.build:build
    jsmin = jstools.jsmin:minify
    """,
    test_suite='nose.collector',
    )

virtualenv = Bunch(
        script_name="install.py",
        packages_to_install=["nose", "http://github.com/whitmo/jstools/tarball/master#egg=jstools"],
        ) 

options(setup=jstools_bunch, virtualenv=virtualenv)

@task
@cmdopts([("uninstall", "u", "undo develop linking")])
def develop():
    """Install all dependencies and develop install jstools"""
    call_task("setuptools.command.develop")    



