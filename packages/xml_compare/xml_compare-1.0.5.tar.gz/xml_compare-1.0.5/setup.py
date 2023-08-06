# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
      name='xml_compare',
      version='1.0.5',
      description='''xml_compare is a XML tree comparer.''',
      long_description='''The xml_compare library allows to easily test two xml trees if they
have the same content. This is especially valuable when unit testing
XML based sistems. 

If the trees differ, xml_compare tries to give a good indication on
the nature and location of difference.

It should work with any etree implementation, but it has been developed
with lxml.''',
#      author='Agustin Villena, Marijn Vriens et al.',
      maintainer="Marijn Vriens",
      maintainer_email="marijn+xmlcompare@metronomo.cl",
      license='BSD', 
      keywords='xml compare library testing',
      install_requires=[
        "lxml",
      ],
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries",
                   "Topic :: Software Development :: Testing",
                   "Topic :: Text Processing :: Markup :: XML"],
      py_modules=['xml_compare'],
)
