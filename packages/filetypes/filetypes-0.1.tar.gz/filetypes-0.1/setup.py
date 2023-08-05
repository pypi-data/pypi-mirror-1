#!/usr/bin/env python

from distutils.core import setup

long_description = '''
The filetypes module will be able to tell you what group a certain file
will belong to, and will give you an additional description.

You can search for both common and uncommon file types.
'''

setup(name='filetypes',
      version='0.1',
      description='Filetypes Metadata',
      long_description=long_description,
      author='Wijnand Modderman',
      author_email='wijnand@wijnand.name',
      url='http://tehmaze.com/code/python/filetypes/',
      packages=['filetypes'],
      package_dir={'filetypes': 'src/filetypes/'},
     )
