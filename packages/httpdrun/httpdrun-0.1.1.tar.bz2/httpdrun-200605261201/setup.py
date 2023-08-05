from distutils.core import setup

setup(name = "httpdrun",
    version = "0.1.1",
    description = "Apache2 Utility",
    author = "Alexandre Girao",
    author_email = "alexgirao@gmail.com",
    url = "http://nextt.org",
    license = "MIT License",
    long_description = """\
  The httpdrun project is intended to automate
development and testing of projects with apache.

  It supports full apache configuration 
abstraction using only python, autogenerate
httpd.conf and autodetect apache installation 
and available modules.
""",
    packages = [
        'httpdrun', 
        'httpdrun.win'
        ],
    package_data = {'httpdrun': ['test/*.py']},
    )
