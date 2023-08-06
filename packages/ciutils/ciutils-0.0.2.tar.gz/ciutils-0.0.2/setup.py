
from setuptools import setup

setup(name="ciutils",
      description="Helpers to use in CI environments (e.g. use xmlrunner together with `test` command) ",
      author="Olemis Lang",
      author_email="olemis+py@gmail.com",
      version="0.0.2",
      install_requires=['unittest-xml-reporting'],
      py_modules=['ciutils'])

