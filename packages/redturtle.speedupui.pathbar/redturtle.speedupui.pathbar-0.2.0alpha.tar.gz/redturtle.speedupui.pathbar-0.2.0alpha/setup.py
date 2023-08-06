from setuptools import setup, find_packages
import os

version = '0.2.0'

setup(name='redturtle.speedupui.pathbar',
      version=version,
      description="A Plone pathbar (breadcrumbs) viewlet implementation with more interactive features",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone pathbar breadcrumbs speedupui redturtle',
      author='Luca Fabbri (keul)',
      author_email='luca.fabbri@redturtle.net',
      url='http://svn.plone.org/svn/collective/redturtle.speedupui.pathbar',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['redturtle', 'redturtle.speedupui'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
