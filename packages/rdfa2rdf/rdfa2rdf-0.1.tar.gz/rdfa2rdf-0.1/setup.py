"""setup - setuptools based setup for rdfa2rdf

Based on Luke Arno's <luke.arno@gmail.com> hatom2atom proxy

http://lukearno.com/projects/hatom2atom/ 

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to:

The Free Software Foundation, Inc., 
51 Franklin Street, Fifth Floor, 
Boston, MA  02110-1301, USA.

Martin McEvoy can be found at http://weborganics.co.uk/
"""

from setuptools import setup, find_packages
from glob import glob

desc = 'WSGI proxy for transforming RDFa to RDF via RDFa2RDFXML.xsl.'

setup(name='rdfa2rdf',
      version='0.1',
      description=desc,
      long_description=desc,
      author='Luke Arno, this version Martin McEvoy',
      author_email='luke.arno@gmail.com, martin@weborganics.co.uk',
      url='http://tools.weborganics.co.uk',
      license="GPL2",
      install_requires="flup\nkid >= 0.8",
      packages = find_packages(),
      data_files=[('kid', glob('kid/*.kid'))],
      entry_points={'console_scripts':['r2rserve = rdfa2rdf.r2rproxy:run']},
      keywords="RDRa RDF wsgi proxy",
      classifiers=[
          'Development Status :: 1 - Alpha',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Text Processing :: Markup :: XML',
          'Topic :: Text Processing :: Markup :: HTML',])

