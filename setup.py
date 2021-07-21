from setuptools import setup, find_packages

setup(
    name='webserver',
    version='0.1.0',
    packages=find_packages(include=['webserver', 'webserver.*']),
    entry_points={
        'console_scripts': [
            'webserver-cli = webserver.__main__:main',
        ]
    }
)
