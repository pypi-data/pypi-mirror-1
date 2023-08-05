import os
from setuptools import setup, find_packages

setup(
    name="z3c.pluggabletemplates",
    version="0.2",
    install_requires=['setuptools'],
    packages=find_packages('src'),
    package_dir= {'':'src'},

    namespace_packages=['z3c'],
    package_data = {
    '': ['*.txt', '*.zcml'],
    },


    # metadata for upload to PyPi
    author='Kevin Smith',
    author_email='kevin@mcweekly.com',
    url="http://code.google.com/p/pluggabletemplates/",
    description="Allows seperation of view code from skin templates like z3c.viewtemplate, but also allows multiple templates to be plugged into your view code.",
    long_description=(
    open('./src/z3c/pluggabletemplates/README.txt').read()
    + '\n' +
    open('./src/z3c/pluggabletemplates/CHANGES.txt').read()),
    license='ZPL 2.1',
    keywords="zope zope3 template",
    zip_safe=False,
    classifiers = ['Framework :: Zope3'],
    )
