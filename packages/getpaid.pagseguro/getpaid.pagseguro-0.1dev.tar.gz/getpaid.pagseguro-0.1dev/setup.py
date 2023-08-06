from setuptools import setup, find_packages
import os

version = '0.1dev'

setup(name='getpaid.pagseguro',
      version=version,
      description="Get Paid payment processor for pagseguro",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("src", "docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: Zope Public License", 
        "Operating System :: OS Independent",
        ],
      keywords='getpaid processor pagseguro',
      author='Get Paid Development Team and Cooperativa Inverta',
      author_email='rafael@inverta.com.br',
      url='http://www.plonegetpaid.com/',
      license='ZPL2.1',
      packages=find_packages('src'),
      package_dir={'':'src'},
      namespace_packages=['getpaid'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      )
