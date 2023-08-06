# vim:fileencoding=utf-8
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import os.path
from setuptools import setup, find_packages

setup(name='gocept.lockd',
      version='0.1',
      description="A simple XML-RPC-based lock daemon to support fencing.",
      long_description=open(
          os.path.join('gocept', 'lockd', 'README.txt')).read(),
      author="Christian Theune",
      author_email="ct@gocept.com",
      license="ZPL 2.1",
      package_dir={'': '.'},
      packages=find_packages('.'),
      include_package_data=True,
      namespace_packages=['gocept'],
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zc.lockfile',
      ],
      entry_points="""
        [console_scripts]
        lockd = gocept.lockd.lockd:main
        lockcmd = gocept.lockd.client:main
      """,
      )
