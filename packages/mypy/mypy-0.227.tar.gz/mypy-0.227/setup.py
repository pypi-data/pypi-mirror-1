from setuptools import setup, find_packages

version = '0.227'

setup(
    name="mypy",
    version=version,
    description="A wsgi framework",
    long_description=""" """,
    author="zsp",
    include_package_data=True,
    zip_safe=False,
    author_email="zsp007@gmail.com",
    packages=find_packages(),
    install_requires = ['decorator','hmako','mako','sqlbean>=0.44','weberror'],
)
