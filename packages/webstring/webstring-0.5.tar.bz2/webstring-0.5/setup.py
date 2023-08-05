# Copyright (c) 2006 L. C. Rees.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1.  Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 2.  Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 3.  Neither the name of the Portable Site Information Project nor the names
# of its contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

'''setup - setuptools based setup for webstring'''

import ez_setup
ez_setup.use_setuptools()

try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(name='webstring',
      version='0.5',
      description='''Template engine that uses Python as the template language''',
      long_description='''A template engine that uses Python as the template language.''',
      author='L. C. Rees',
      author_email='lcrees@gmail.com',
      url='http://psilib.sourceforge.net/webstring.html',
      license='BSD',
      packages = ['webstring', 'webstring.ext', 'webstring.tests'],
      zip_safe = True,
      keywords='template text XML HTML XHTML meld TurboGears WSGI',
      classifiers=['Development Status :: 4 - Beta',
                    'Environment :: Web Environment',
                    'Intended Audience :: Developers', 
                    'Framework :: TurboGears',
                    'License :: OSI Approved :: BSD License',
                    'Natural Language :: English',
                    'Operating System :: OS Independent',
                    'Programming Language :: Python',
                    'Topic :: Internet :: WWW/HTTP',
                    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                    'Topic :: Text Processing',
                    'Topic :: Text Processing :: Markup :: HTML',
                    'Topic :: Text Processing :: Markup :: XML'],
      entry_points='''
      [python.templating.engines]
      webstring = webstring.ext.turbogears:TurboWebstring
      lwebstring = webstring.ext.turbogears:TurboWebstring
      ''',
      install_requires = ['cElementTree', 'elementtree', 'lxml'])