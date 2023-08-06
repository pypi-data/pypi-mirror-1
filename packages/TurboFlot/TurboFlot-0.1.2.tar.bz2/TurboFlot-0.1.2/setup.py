import os
__requires__="TurboGears"
from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

packages=find_packages()
package_data = find_package_data(where='turboflot', package='turboflot')

setup(
    name="TurboFlot",
    version="0.1.2",
    description="A TurboGears widget for Flot, a jQuery plotting library",
    author="Luke Macken",
    author_email="lewk@csh.rit.edu",
    license="MIT",
    install_requires=[
        "TurboGears >= 1.0.3.2",
    ],
    scripts=[],
    data_files=[
        'turboflot/static/excanvas.js',
        'turboflot/static/jquery.flot.js',
        'turboflot/static/jquery.js',
        'turboflot/static/turboflot.css',
    ],
    zip_safe=False,
    packages=packages,
    package_data=package_data,
    keywords=[
        'turbogears.widgets',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Widgets',
    ],
    entry_points = """
        [turbogears.widgets]
        turboflot = turboflot.widgets
    """
)
