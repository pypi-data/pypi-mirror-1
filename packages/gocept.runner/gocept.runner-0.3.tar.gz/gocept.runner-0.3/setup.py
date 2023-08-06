import os.path
from setuptools import setup, find_packages

def read(*names):
    return open(os.path.join(os.path.dirname(__file__), *names), 'r').read()

setup(name='gocept.runner',
      version='0.3',
      description="Create stand alone programs with full ZCA",
      long_description=(
          read('src', 'gocept', 'runner', 'appmain.txt')
          + '\n\n'
          + read('src', 'gocept', 'runner', 'once.txt')
          + '\n\n'
          + read('src', 'gocept', 'runner', 'README.txt')
          + '\n\n'
          + read('CHANGES.txt')
      ),
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers = (
          "Topic :: Software Development",
          "Framework :: Zope3",
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved",
          "License :: OSI Approved :: Zope Public License",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
      ),
      keywords="zope3 mainloop",
      author="gocept gmbh & co. kg",
      author_email="mail@gocept.com",
      url="",
      license="ZPL 2.1",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'zope.app.twisted',
          'zope.app.wsgi',
          'zope.testing',
      ],
      extras_require=dict(
          test=['zope.securitypolicy',
                'zope.app.testing',
                'zope.app.zcmlfiles']),
      entry_points = dict(
        console_scripts =
          ['runexample = gocept.runner.example:example'])
     )
