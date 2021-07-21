from setuptools import setup, find_packages

setup(
    name='web_server',
    version='0.1.0',
    packages=find_packages(include=['web_server', 'web_server.*']),
    entry_points={
        'console_scripts': [
            'web-server-cli = web_server.__main__:main',
        ]
    }
)