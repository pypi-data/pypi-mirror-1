#!/usr/bin/env python

from distutils.core import setup

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
files = ["library/*"]

setup(name = "kernelcheck",
    version = "1.1.4",
    description = "Build the latest kernel",
    author = "Master Kernel",
    author_email = "master.kernel.contact@gmail.com",
    url = "http://kcheck.sf.net",
    #Name the folder where your packages live:
    #(If you have other packages (dirs) or modules (py files) then
    #put them into the package directory - they will be found 
    #recursively.)
    packages = ['KernelCheck'],
    license = "GNU GPLv3",
    #'package' package must contain files (see list above)
    #I called the package 'package' thus cleverly confusing the whole issue...
    #This dict maps the package name =to=> directories
    #It says, package *needs* these files.
    package_data = {'KernelCheck' : files },
    data_files=[('share/kernelcheck/pixmaps', ['KernelCheck/library/kernelcheckicon.svg']),
                ('share/applications', ['KernelCheck/library/kernelcheck.desktop'])],
    #'runner' is in the root.
    scripts = ["kernelcheck"],
    long_description = """Build the latest kernel with the click of a button""" ,
    #
    #This next part it for the Cheese Shop, look a little down the page.
    classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Environment :: X11 Applications :: GTK',
      'Intended Audience :: End Users/Desktop',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License (GPL)',
      'Operating System :: POSIX :: Linux',
      'Programming Language :: Python',
      'Topic :: Desktop Environment'
      ]
) 
