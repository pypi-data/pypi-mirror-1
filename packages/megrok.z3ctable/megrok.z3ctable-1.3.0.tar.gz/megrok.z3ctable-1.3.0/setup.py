from setuptools import setup, find_packages
import os

version = '1.3.0'
readme = open(os.path.join("src", "megrok", "z3ctable", "README.txt")).read()
history = open(os.path.join("docs", "HISTORY.txt")).read()

setup(name='megrok.z3ctable',
      version=version,
      description="A table component package for Grok based on z3c.table.",
      long_description= u"%s\n\n%s" % (readme, history),
      classifiers=[
          "Framework :: Zope3",
          "Programming Language :: Python",
          "Programming Language :: Zope",
          "Intended Audience :: Developers",
          "Development Status :: 4 - Beta",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='grok table zope3',
      author='Christian Klinger',
      author_email='cklinger@novareto.de',
      url='http://pypi.python.org/pypi/megrok.z3ctable',
      license='GPL',
      package_dir={'':'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
	  'grokcore.component',
          'grokcore.view',
          'z3c.table',
	  'megrok.layout',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
