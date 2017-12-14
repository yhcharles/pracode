from setuptools import setup

setup(
    name='pracode',
    version='0.1.0',
    description='tool for practicing coding skills against coding websites, e.g. leetcode, etc.',
    classifiers=[
        'Programming Language :: Python :: 3 :: Only'
    ],
    url='https://github.com/yhcharles/pracode',
    author='Charlie Yan',
    packages=['pracode'],
    install_requires=[
        'sh',
        'ansicolors',
    ],
    entry_points = {
        'console_scripts': ['pracode=pracode.main:main'],
    }
)
