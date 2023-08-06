from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='Products.ATTalesExpressionCriterion',
      version=version,
      description="Smart folder criterion that stores TALES Expressions.",
      long_description=open("Products/ATTalesExpressionCriterion/README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        ],
      keywords='ATContentTypes Collection Topic Criterion',
      author='Andreas Gabriel',
      author_email='gabriel@hrz.uni-marbug.de',
      url='http://svn.plone.org/svn/collective/Products.ATTalesExpressionCriterion',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Products.TemplateFields',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
