#
# This file is part of Dragonfly.
# (c) Copyright 2007, 2008 by Christo Butcher
# Licensed under the LGPL.
#
#   Dragonfly is free software: you can redistribute it and/or modify it 
#   under the terms of the GNU Lesser General Public License as published 
#   by the Free Software Foundation, either version 3 of the License, or 
#   (at your option) any later version.
#
#   Dragonfly is distributed in the hope that it will be useful, but 
#   WITHOUT ANY WARRANTY; without even the implied warranty of 
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
#   Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public 
#   License along with Dragonfly.  If not, see 
#   <http://www.gnu.org/licenses/>.
#

"""
Dragonfly -- a speech recognition framework
============================================================================

Dragonfly offers a powerful Python interface to speech 
recognition and a high-level language object model to easily 
create and use voice commands.  Dragonfly supports following 
speech recognition engines:

 - Dragon NaturallySpeaking (DNS), a product of *Nuance*
 - Windows Speech Recognition (WSR), included with Microsoft 
   Windows Vista and freely available for Windows XP


Basic example
----------------------------------------------------------------------------

A very simple example of Dragonfly usage is to create a static 
voice command with a callback that will be called when the 
command is spoken.  This is done as follows:

.. code-block:: python

   from dragonfly.all import Grammar, CompoundRule

   class ExampleRule(CompoundRule):

       spec = "do something computer"

       def _process_recognition(self, node, extras):
           print "Voice command spoken."

   grammar = Grammar("example grammar")
   grammar.add_rule(ExampleRule())
   grammar.load()

The example above is very basic and doesn't show any of 
Dragonfly's exciting features, such as dynamic speech elements. 
To learn more about these, please take a look at the project's 
documentation `here
<http://dragonfly.googlecode.com/svn/trunk/dragonfly/documentation/index.html>`_.

"""


import os.path, re
from setuptools import setup


#---------------------------------------------------------------------------
# Gather version from distribution file.

directory = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(directory, "version.txt")
version_string = open(path).readline()
match = re.match(r"\s*(?P<rel>(?P<ver>\d+\.\d+)(?:\.\S+)*)\s*", version_string)
version = match.group("ver")
release = match.group("rel")


#---------------------------------------------------------------------------
# Set up package.

setup(
      name          = "dragonfly",
      version       = release,
      description   = "Speech recognition framework",
      author        = "Chris Butcher",
      author_email  = "dist.dragonfly@twizzy.biz",
      license       = "LGPL",
      url           = "http://code.google.com/p/dragonfly/",
      zip_safe      = False,  # To unzip documentation files.
      long_description = __doc__,

      classifiers=[
                   "Environment :: Win32 (MS Windows)",
                   "Development Status :: 4 - Beta",
                   "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
                   "Operating System :: Microsoft :: Windows",
                   "Programming Language :: Python",
                  ],

      packages=[
                "dragonfly",
                "dragonfly.actions",
                "dragonfly.engines",
                "dragonfly.grammar",
                "dragonfly.windows",
               ],
     )
