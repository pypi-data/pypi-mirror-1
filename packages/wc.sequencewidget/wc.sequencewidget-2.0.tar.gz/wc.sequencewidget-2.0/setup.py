from setuptools import setup, find_packages

setup(name='wc.sequencewidget',
      version='2.0',
      url='http://worldcookery.com/Downloads',
      description='Alternate sequence widget for the Zope 3 form framework',
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
