import os
import sys

from setuptools import setup, find_packages

execfile(os.path.join("tw", "extjs", "release.py"))

setup(
    name=__PROJECT__,
    version=__VERSION__,
    description=__DESCRIPTION__,
    author=__AUTHOR__,
    author_email=__EMAIL__,
    url=__URL__,
    install_requires=[
        "ToscaWidgets >= 0.9.1",
        ],
    download_url = "http://toscawidgets.org/download",
    packages=find_packages(exclude=['ez_setup', 'tests', 'tw.extjs.tests']),
    namespace_packages = ['tw'],
    zip_safe=True,
    include_package_data=True,
    test_suite = 'nose.collector',
    entry_points="""
        [toscawidgets.widgets]
        widgets = tw.extjs
        samples = tw.extjs.samples
    """,
    keywords = [
        'toscawidgets.widgets',
    ],
)
