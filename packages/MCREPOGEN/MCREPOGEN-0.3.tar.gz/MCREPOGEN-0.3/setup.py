#!/usr/bin/env python
# Copyright 2009 Neil Martinsen-Burrell

# This file is part of mcrepogen
#
# mcrepogen is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from mcrepogen.version_info import version_str

import os
from distutils.core import setup

# regenerate this every time
if os.path.exists('MANIFEST'): os.remove('MANIFEST')

setup(name='MCREPOGEN',
      version=version_str,
      description='Markov Chain Repository Generator',
      long_description="""\
MCREPOGEN generates random version control histories. It uses a Markov Chain
model to generate successive states of a directory tree. You can generate as
many revisions as you want and the output is in the standard fast-import
format. This means that MCREPOGEN-generated histories can be imported into many
different version control systems to provide examples for testing.
""",
      author='Neil Martinsen-Burrell',
      author_email='nmb@wartburg.edu',
      url='http://launchpad.net/mcrepogen',
      download_url='http://launchpad.net/mcrepogen/+download',
      requires=['bzr', 'Numpy'],

      scripts=['gen_random_history.py'],
      packages=['mcrepogen', 'mcrepogen.tests'],
      package_data={'mcrepogen' : ['6of12.txt.gz']},
      package_dir={'mcrepogen' : 'mcrepogen'},

      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Programming Language :: Python :: 2',
                   'Topic :: Software Development :: Version Control',
                  ],
     )


