from setuptools import setup, find_packages

setup(name='wc.sqlrecipe',
      version='3.8',
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
                        'z3c.zalchemy==0.2',
                        'SQLAlchemy>=0.3.9,<0.4dev',
                        'pysqlite',  # this dependency should become optional
                        'rwproperty'],
      )
