# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from setuptools import setup, find_packages

setup(name='gocept.httop' ,
      version="1.0",
      author="Christian Theune",
      author_email="ct@gocept.com",
      description="An ncurses-based tool to monitor website "
                  "responsiveness in real-time.",
      long_description=open('README.txt').read(),
      license="ZPL 2.1",
      zip_safe=False,
      packages=find_packages('src'),
      include_package_data=True,
      package_dir={'':'src'},
      namespace_packages=['gocept'],
      install_requires=['setuptools'],
      entry_points = """
          [console_scripts]
          httop = gocept.httop.main:main
          """)
