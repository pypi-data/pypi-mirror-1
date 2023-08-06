from setuptools import setup, find_packages

version = '0.13'

setup(
    name="mypy",
    version=version,
    description="A wsgi framework",
    long_description=""" """,
    author="zsp",
    author_email="zsp007@gmail.com",
    packages=find_packages(),
    install_requires = ['decorator','hmako','mako','yaro','static','sqlbean','weberror'],
)
