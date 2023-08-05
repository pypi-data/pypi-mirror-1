from setuptools import setup, find_packages

setup(name='wc.sqlrecipe',
      version='2.8',
      url='http://worldcookery.com/Downloads',
      description="SQL-based implementation of WorldCookery's Recipe "
                  "content object",
      author='Philipp von Weitershausen',
      author_email='philipp@weitershausen.de',
      long_description=file('README.txt').read(),
      classifiers=['Development Status :: 4 - Beta',
                   'Framework :: Zope3',
                   'Intended Audience :: Developers'],
      packages=find_packages(),
      namespace_packages=['wc',],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'SQLAlchemy',
                        'z3c.zalchemy',
                        'pysqlite',  # this dependency should become optional
                        'rwproperty'],
      )
