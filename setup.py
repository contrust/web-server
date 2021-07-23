from setuptools import setup, find_packages

setup(
    name='webserver',
    version='0.1.0',
    packages=find_packages(include=['webserver', 'webserver.*']),
)
