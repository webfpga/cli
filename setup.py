#!/usr/bin/env python
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='webfpga',  
    version='0.2',
    scripts=['webfpga'] ,
    author="WebFPGA",
    author_email="support@webfpga.io",
    description="Official WebFPGA Command-line Utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/webfpga/cli",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
