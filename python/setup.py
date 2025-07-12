from setuptools import setup, find_packages
import os


def read_file(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding="utf-8").read()


setup(
    name="spider_client",
    version="0.1.55",
    url="https://github.com/spider-rs/spider-clients/tree/main/python",
    license="MIT",
    author="Spider",
    author_email="jeff@spider.cloud",
    description="Python SDK for Spider Cloud API",
    packages=find_packages(),
    install_requires=["requests", "ijson", "tenacity", "aiohttp"],
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
        "Operating System :: OS Independent",
    ],
)
