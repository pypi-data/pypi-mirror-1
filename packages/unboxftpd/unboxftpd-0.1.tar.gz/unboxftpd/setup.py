#!/usr/bin/env python
from distutils.core import setup
import os

name = 'unboxftpd'
version = '0.1'

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk(name):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[len(name + os.sep):]
        for f in filenames:
            data_files.append(os.path.join(prefix, f))

setup(name=name,
      version=version,
      description='A FTP server application for Django',
      long_description="unboxftpd add FTP server to your Django project easily.",
      author='Shinya Okano',
      author_email='tokibito@gmail.com',
      url='http://bitbucket.org/tokibito/unboxftpd/',
      download_url='http://bitbucket.org/tokibito/unboxftpd/get/0.1.gz',
      packages=packages,
      package_data={'unboxftpd': data_files},
      keywords=['ftp', 'server', 'ftpd', 'django', 'python'],
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Environment :: Console',
                   'Framework :: Django',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Internet :: File Transfer Protocol (FTP)',
                   ],
      )
