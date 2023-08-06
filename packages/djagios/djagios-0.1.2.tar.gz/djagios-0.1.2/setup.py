import sys
import os
import glob

from distutils.core import setup


def add_folder(source):
    s = set()
    for path in os.listdir(source):
        tpath = os.path.join(source,path)
        if os.path.isfile(tpath):
            s.add(tpath)
        elif os.path.isdir(tpath):
            s = s.union(add_folder(tpath))
    return list(s)

data_files = [
        ('templates', add_folder(os.path.abspath('djagios/templates'))),
        ('media', add_folder(os.path.abspath('djagios/media'))),
        ]
print data_files

setup(
    name = "djagios",
    version = "0.1.2",
    packages = ['djagios','djagios.core', 'djagios.common',],
    data_files = [
        ('/usr/share/djagios-0.1/templates/default', add_folder(os.path.abspath('djagios/templates'))),
        ('/usr/share/djagios-0.1/media/default', add_folder(os.path.abspath('djagios/media'))),
        ],
    author = "Jochen Maes",
    author_email = "sejo@djagios.org",
    description = "A package to help configure nagios written in Django",
    url = "http://djagios.org/",
    license = 'GPL2',
)





