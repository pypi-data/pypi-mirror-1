from distutils.core import setup

setup(name='hgexternals',
      version='0.2',
      author='Tarek Ziade',
      author_email='tarek@ziade.org',
      url='http://bitbucket.org/tarek/hgexternals',
      description='Mercurial extension to simulate Subversion externals',
      long_description=open('README.txt').read(),
      license='BSD',
      keywords='mercurial hg version',
      py_modules = ['hgexternals'],
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'Topic :: Software Development :: Version Control',
                   ]
      )
