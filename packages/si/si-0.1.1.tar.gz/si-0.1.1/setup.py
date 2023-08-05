from setuptools import setup

setup(
        name = "si",
        version = "0.1.1",
        packages = ["si", "si.units", "si.mathmodules", "si.pylab"],
        author = "chrysn",
        author_email = "chrysn@fsfe.org",
        description = "Module to represent SI units",
        license = "GPL",
        zip_safe = True,
        test_suite = "test.all",
        )
