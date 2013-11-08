#!/usr/bin/env python

from setuptools import setup, find_packages

import madjango


def reqs(*f):
    return list(filter(None, [strip_comments(l) for l in open(
        os.path.join(os.getcwd(), 'requirements', *f)).readlines()]))

install_requires = reqs('default.txt')

setup(
    name='madjango',
    version=".".join(map(str, madjango.__version__)),
    author='Dino Petrone + Adam Venturella',
    author_email='dinopetrone@gmail.com',
    maintainer="BLITZ",
    maintainer_email="",
    url='https://github.com/blitzagency/django-magento-auth',
    install_requires=install_requires,
    description = 'A pluggable Django middleware for magento auth',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
)
