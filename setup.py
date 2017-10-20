from setuptools import setup

setup(
    name='pracode',
    description='tool for practicing coding skills against coding websites, e.g. leetcode, etc.',
    classifiers=[
        'Programming Language :: Python :: 3 :: Only'
    ],
    url='https://github.com/yhcharles/pracode',
    author='Charlie Yan',
    packages=['pracode'],
    install_requires=[
        'requests',
        'bs4',
        'browser_cookies3',
    ],
    entry_points = {
        'console_scripts': ['pracode=pracode.main:main'],
    }
)
