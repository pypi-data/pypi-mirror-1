#!/usr/bin/env python
import os
from setuptools import setup

here = os.path.dirname(__file__)
changes_file = os.path.join(here, 'NEWS.txt')
changes_in_latest_version = file(changes_file).read().split('\n\n\n', 1)[0]

setup(
    name='gtimelog',
    version='0.2.1',
    author='Marius Gedminas',
    author_email='marius@gedmin.as',
    url='http://mg.pov.lt/gtimelog/',
    description='A Gtk+ time tracking application',
    long_description=changes_in_latest_version,
    license='GPL',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: X11 Applications :: GTK',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Topic :: Office/Business',
    ],

    packages=['gtimelog'],
    package_dir={'gtimelog': 'src/gtimelog'},
    package_data={'gtimelog': ['*.glade', '*.png']},
    test_suite='gtimelog.test_gtimelog',
    zip_safe=False,
    entry_points="""
    [console_scripts]
    gtimelog = gtimelog.gtimelog:main
    """,
# This is true, but pointless, because easy_install PyGTK chokes and dies
#   install_requires=['PyGTK'],
)
