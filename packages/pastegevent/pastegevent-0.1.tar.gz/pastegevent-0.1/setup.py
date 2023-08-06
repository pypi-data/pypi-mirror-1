from setuptools import setup, find_packages
import sys, os


here = os.path.dirname(__file__)

version = "0.1"
long_description = open(os.path.join(here, "README"), "rb").read()


setup(name="pastegevent",
      version=version,
      description="Run WSGI applications with PasteDeploy and gevent.",
      long_description=long_description,
      classifiers=[
          "Environment :: Plugins",
          "Framework :: Paste",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP :: HTTP Servers"
      ],
      keywords="paste wsgi gevent",
      author="Andrey Popp",
      author_email="8mayday@gmail.com",
      url="",
      license="MIT",
      packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
      zip_safe=True,
      install_requires=[
          "gevent",
          "greenlet",
          "PasteDeploy"
      ],
      entry_points="""
      [paste.server_factory]
      gevent = pastegevent.server:server_factory
      gevent_patched = pastegevent.server:server_factory_patched
      """,
      )
