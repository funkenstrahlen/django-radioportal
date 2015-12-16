# -*- encoding: utf-8 -*-
# 
# Copyright © 2012 Robert Weidlich. All Rights Reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# 
# 3. The name of the author may not be used to endorse or promote products
# derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE LICENSOR "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
# OF SUCH DAMAGE.
# 
import os
import codecs
from setuptools import setup


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


setup(name='django-radioportal',
      description='Application for aggregating shows, their episodes and streams',
      long_description=read("README.md"),
      use_scm_version=True,
      setup_requires=['setuptools_scm'],
      author='Robert Weidlich',
      author_email='github@robertweidlich.de',
      url='https://github.com/xenim/django-radioportal',
      packages=['radioportal'],
      include_package_data=True,
      install_requires=[
        "Django < 1.9",
        "Pillow <= 2.9.0",
        "amqplib <= 1.0.2",
        "anyjson <= 0.3.3",
        "carrot <= 0.10.7",
        "django-autoslug <= 1.8.0",
        "django-guardian <= 1.3",
        "django-hosts <= 1.2",
        "django-readonlywidget <= 0.2",
        "django-shorturls",
        "django-shorturls-external",
        "python-dateutil <= 2.4.2",
        "simplejson <= 3.7.3",
        "translitcodec <= 0.4.0",
        "vobject <= 0.6.6",
        "django-jsonfield <= 0.9.13",
        "django-tastypie <= 0.12.2"
      ],
      classifiers=[
          'Framework :: Django',
          ],
      )
