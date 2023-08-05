from setuptools import setup, find_packages

setup(name='wc.cookiecredentials',
      version='2.0.1',
      url='http://worldcookery.com/Downloads',
      description='Cookie Credentials plug-in for the Zope Pluggable '
                  'Authentication Utility',
      author='Philipp von Weitershausen',
      author_email='philipp@weitershausen.de',
      long_description=file('README.txt').read(),
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Framework :: Zope3',
                   'Intended Audience :: Developers'],
      packages=find_packages(),
      namespace_packages=['wc',],
      include_package_data=True,
      zip_safe=False,
      )
