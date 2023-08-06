from setuptools import setup, find_packages
import os

version = "0.9"

setup(name="Products.signalstackLogger",
      version=version,
      description="Output zope stacktrace on signal using logging facility",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords="",
      author="Andy Altepeter",
      author_email="aaltepet@altepeter.net",
      url="",
      license="BSD",
      packages=find_packages(exclude=["ez_setup"]),
      namespace_packages=["Products"],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "setuptools",
          "z3c.deadlockdebugger"
      ],
      )
