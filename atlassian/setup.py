# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="atlassian_api",
    version="0.0.1",
    description="Jira and Xray API Library, which will simplify test automation using python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="www.bosch.com",
    author="ETAS VCS TEAM TED TITANS",
    author_email="Be18_CS_CS_MC_TEAM_E2EGAME@bcn.bosch.com",
    license="",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent"
    ],
    packages=["atlassian_api"],
    include_package_data=True,
    install_requires=["requests"]
)