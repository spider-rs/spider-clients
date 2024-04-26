from setuptools import setup, find_packages
import os


def read_file(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding="utf-8").read()


setup(
    name="spider-client",
    version="0.0.10",
    url="https://github.com/spider-rs/spider-clients/tree/main/python",
    author="Spider",
    author_email="jeff@a11ywatch.com",
    description="Python SDK for Spider Cloud API",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
