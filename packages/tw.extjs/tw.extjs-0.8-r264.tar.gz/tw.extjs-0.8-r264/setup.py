import os
import sys
from fnmatch import fnmatchcase
from distutils.util import convert_path

from setuptools import setup, find_packages


def find_package_data( package='', where='.', only_in_packages=True):
    """Finds static resources in package. Adapted from turbogears.finddata."""  
    out = {}
    exclude = ('*.py', '*.pyc', '*~', '.*', '*.bak', '*.swp*')
    exclude_directories = ('.*', 'CVS', '_darcs', './build',
                           './dist', 'EGG-INFO', '*.egg-info')
    stack = [(convert_path(where), '', package, only_in_packages)]
    while stack:
        where, prefix, package, only_in_packages = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        print >> sys.stderr, (
                            "Directory %s ignored by pattern %s"
                            % (fn, pattern))
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                    stack.append((fn, '', new_package, False))
                else:
                    stack.append((fn, prefix + name + '/', package, only_in_packages))
            elif package or not only_in_packages:
                # is a file
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        print >> sys.stderr, (
                            "File %s ignored by pattern %s"
                            % (fn, pattern))
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

execfile(os.path.join("tw", "extjs", "release.py"))

setup(
    name=__PROJECT__,
    version=__VERSION__,
    description=__DESCRIPTION__,
    author=__AUTHOR__,
    author_email=__EMAIL__,
    url=__URL__,
    install_requires=[
        "ToscaWidgets",
        ## Add other requirements here
        # "Genshi",
        ],
    download_url = "http://twtools.googlecode.com/svn/dist/",
    packages=find_packages(exclude=['ez_setup', 'tests', 'tw.extjs.tests']),
    namespace_packages = ['tw'],
    zip_safe=False,
    include_package_data=True,
    test_suite = 'nose.collector',
    package_data= find_package_data('tw.extjs'),
    entry_points="""
        [tw]
        # Use 'widgets' to point to the module where widgets should be imported
        # from to register in the widget browser
        widgets = tw.extjs
        # Use 'samples' to point to the module where widget examples
        # should be imported from to register in the widget browser
        samples = tw.extjs.samples
        # Use 'resources' to point to the module where resources
        # should be imported from to register in the widget browser
        #resources = tw.extjs.resources
    """,
    keywords = [
        'tw',
    ],
)
