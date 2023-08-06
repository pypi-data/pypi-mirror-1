#from setuptools import setup
from distutils.core import setup
import sys
import os
from os.path import basename, dirname, relpath, join
from glob import glob
import telepathy_spyke

version = '0.1'

print "WARNING: Currently only support installing into your home directory."
print "This is because I haven't worked out how to make setuptools play"
print "nice with the xdg basedir spec in the presence of virtualenv and"
print "all other kinds of horrible nonsense."

def data_dir(dest, src):
    """Returns a list of all files in a dir, which can be appended to the 
    data_files argument in setup()
    eg: 
    data_dir('.local/share/empathy/icons/', 'data/icons/')
    """
    ret = []
    def destpath(dirpath):
        return join(dest, relpath(dirpath, src))
    
    for (dirpath, dirnames, filenames) in os.walk(src):
        if filenames:
            filenames = [os.path.join(dirpath, name) for name in filenames]
            ret.append((destpath(dirpath), filenames))

    return ret
        
        
data_files = [('.local/share/telepathy/managers/', ['data/spyke.manager']),
                  ('.local/share/dbus-1/services/', glob('data/*.service')),
                  ('.local/share/mission-control/profiles/', ['data/skype.profile'])
            ]+data_dir('.local/share/empathy/icons/', 'data/icons/')

print data_files

setup(name='spyke',
      version=version,
      description="A skype connection manager.",
      long_description=telepathy_spyke.__doc__ ,# + shiny.test.doctests.__doc__,
      classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.6",
          "Topic :: Communications :: Chat",
          "Topic :: Communications :: Telephony",
          "Topic :: Desktop Environment :: Gnome",
          "Topic :: Desktop Environment :: K Desktop Environment (KDE)",
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='skype telepathy connection manager spyke',
      author='David Laban',
      author_email='alsuren@gmail.com',
      url='https://launchpad.net/spyke',
      license='GPL', #FIXME: this is a really stupid license to be using with skype.
      packages=['spyke'],
      include_package_data=True,
      zip_safe=False,
      requires=['shiny'],
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      #test_suite = TODO,
      entry_points="""
      # -*- Entry points: -*-
      """,
      scripts=['telepathy_spyke.py'],
      data_files=data_files,
      
      )
