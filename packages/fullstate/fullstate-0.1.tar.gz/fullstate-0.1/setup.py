# --*-- coding:iso8859-1 --*--
# Date: $Date: 2009-10-31 14:54:49 +0200 (la, 31 loka 2009) $
# Revision: $Revision: 8 $
# Author: $Author: eino.makitalo $
# Url:  $HeadURL: https://fullstate.googlecode.com/svn/trunk/setup.py $
from distutils.core import setup
setup(name='fullstate',
      version='0.1',
      description='Minimalistic prevayler-like memory based data structure with ACID',
      author='Eino Mäkitalo',
      author_email='eino.makitalo@gmail.com',
      url='http://code.google.com/p/fullstate/', 
      license='MIT License',
      platforms='Any',
      packages=['fullstate'],
      classifiers = [
	'License :: OSI Approved :: MIT License',
	'Development Status :: 4 - Beta',
	'Programming Language :: Python :: 2.6',
	'Programming Language :: Python :: 3',
      ],
      )
