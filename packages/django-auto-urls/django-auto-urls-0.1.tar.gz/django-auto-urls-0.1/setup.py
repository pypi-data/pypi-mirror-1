#!/usr/bin/env python
from distutils.core import setup

setup(
      name='django-auto-urls',
      version='0.1',
      author='Mikhail Korobov',
      author_email='kmike84@gmail.com',
      url='http://bitbucket.org/kmike/django-auto-urls/',      
      
      description = "Django app that try to load template by it's file name passed in url.",
      long_description = """ Django app that try to load template by it's file 
                             name passed in url. It is useful in development for quick template 
                             rendering without overhead of defining urls for each template. 
                             It may be helpful for work with designers as designers will be 
                             able to write Django templates (with inheritance and all the 
                             template tags) instead of raw HTML and don't care about writing 
                             views and urlconfs. Do not use it in production as this approach 
                             is insecure.
                         """,
      license = 'MIT License (http://www.opensource.org/licenses/mit-license.php)',
      packages=['auto_urls'],
      
      classifiers=(
          'Development Status :: 3 - Alpha',
          'Environment :: Plugins',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Natural Language :: Russian',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules'
        ),
)