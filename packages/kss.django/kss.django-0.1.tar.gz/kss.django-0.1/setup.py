from setuptools import setup, find_packages

version = '0.1'

long_description = """
KSS enables you write rich Ajax applications without having to code
Javascript. It does this by using a CSS like resource, this is called
a KSS file. All that you as a developer need to do is write files like
these and implement server side Python.

This package contains the components needed for Django. It allows
Django developers to use the KSS system in their applications.
"""


setup(name='kss.django',
      version=version,
      description="KSS for Django",
      long_description="""\
""",
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[], 
      keywords="",
      author="",
      author_email="",
      url="",
      license="",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'kss.base',
                        ],
      )
