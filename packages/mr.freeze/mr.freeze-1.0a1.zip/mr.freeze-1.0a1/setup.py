from setuptools import setup, find_packages
import os

version = "1.0a1"

setup(name="mr.freeze",
      version=version,
      description="Trigger various actions on a running zope via a USR1 signal",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Framework :: Zope2",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords="zope debugging pdb",
      author="David Glick",
      author_email="davidglick@onenw.org",
      url="http://en.wikipedia.org/wiki/Mr._Freeze",
      license="BSD",
      packages=find_packages(exclude=["ez_setup"]),
      namespace_packages=["mr"],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "setuptools",
          "z3c.deadlockdebugger"
      ],
      )
