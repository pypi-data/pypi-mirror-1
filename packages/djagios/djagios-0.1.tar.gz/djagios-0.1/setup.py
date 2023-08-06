import sys
import os
import glob

#from distutils.core import setup
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages


def add_folder(source):
    s = set()
    for path in os.listdir(source):
        tpath = os.path.join(source,path)
        if os.path.isfile(tpath):
            s.add(tpath)
        elif os.path.isdir(tpath):
            s = s.union(add_folder(tpath))
    return s

setup(
    name = "djagios",
    version = "0.1",
    packages = ['djagios','djagios.core', 'djagios.common',],
    #data_files = [
    #    ('share/djagios/templates', add_folder(os.path.abspath('djagios/templates'))),
    #    ('share/djagios/media', add_folder(os.path.abspath('djagios/media'))),
    #    ],
    author = "Jochen Maes",
    author_email = "sejo@djagios.org",
    description = "A package to help configure nagios written in Django",
    url = "http://djagios.org/",
    include_package_data = True,
    setup_requires = ['setuptools_git',],
    install_requires = ['Django >=1.1 , ==dev' ,],
    license = 'GPL2',
)




