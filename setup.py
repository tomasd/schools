#!/usr/bin/python2.6
from setuptools import setup, find_packages
from distutils.command.build_py import build_py

#
# modify build process to exclude specific files from the build
#
find_package_modules_old = build_py.find_package_modules

def find_package_modules(self, package, package_dir):
    excludes = [
        ('schools', 'local_settings', 'src/schools/local_settings.py'),
    ] 

    modules = find_package_modules_old(self, package, package_dir)
    for pkg, module, fname in excludes:
        if (pkg, module, fname) in modules:
            modules.remove((pkg,module,fname))
            print "excluding pkg = %s, module = %s, fname = %s" % \
                (pkg,module,fname)
    return modules

build_py.find_package_modules = find_package_modules

setup(
      name='schools',
      version='0.1',
      packages = find_packages('src', exclude=["*.tests.*", 'tests.*', 'tests',]),
      package_dir = {'':'src'},
      author = "Tomas Drencak",
      author_email = "tomas@drencak.com",
      description = "",
      url = "",
      
      include_package_data = True,
      entry_points = {
       'console_scripts': 'schools = schools.manage:run',
      },
      
)
