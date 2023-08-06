from setuptools import setup, find_packages
import sys, os

here = os.path.dirname(__file__)

version = "0.3"
long_description = \
        open(os.path.join(here, "README"), "rb").read() \
        + "\n" \
        + open(os.path.join(here, "CHANGES"), "rb").read()


setup(name="clipy",
      version=version,
      description="Library for creating command line interfaces",
      long_description=long_description,
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules"
      ],
      keywords="python cli framework cmd command line interface",
      author="Andrey Popp",
      author_email="8mayday@gmail.com",
      url="",
      license="MIT",
      packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
      include_package_data=True,
      zip_safe=True,
      install_requires=[],
      extras_require={
        "argparse": ["argparse"]
      },
      entry_points={
        # This is for testing purposes.
        "clipy.test": ["dummy=clipy.tests:dummy"]
      },
      test_suite="clipy"
      )
