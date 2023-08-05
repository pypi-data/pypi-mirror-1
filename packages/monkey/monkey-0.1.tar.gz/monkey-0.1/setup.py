from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
    name='monkey',
    version=version,
    description="A package that provides tools for guerilla (monkey)-patching.",
    long_description=open("README.txt").read(),
    classifiers=[
    "Topic :: Software Development :: Quality Assurance",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python",
    "Development Status :: 4 - Beta",
    "Topic :: Utilities",
    ],
    keywords='',
    author='Malthe Borch',
    author_email='mborch@gmail.com',
    url='',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    # -*- Extra requirements: -*-
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
    )
