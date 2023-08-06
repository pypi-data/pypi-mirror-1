from setuptools import setup, find_packages
import os

version = "1.0rc1"

setup(name="Products.signalstack",
      version=version,
      description="Show stacktrace on signal",
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
      author="Jarn AS",
      author_email="info@jarn.com",
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
