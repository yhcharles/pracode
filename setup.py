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
    ],
    entry_points = {
        'console_scripts': ['pc=pracode.main:main'],
    }
)
