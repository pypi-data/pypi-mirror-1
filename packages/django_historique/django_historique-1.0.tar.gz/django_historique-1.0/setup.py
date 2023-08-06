from setuptools import setup, find_packages

import sys, os

version = '1.0'

setup(
    name='django_historique',
    version=version,
    description="Save revisions of your objects in another table!",
    long_description="""
""",
    keywords='django, history, diff',
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
    ],
    author='Cyril Robert',
    author_email='cyrilrbt@gmail.com',
    url='http://code.google.com/p/django-historique/',
    download_url='http://pypi.python.org/pypi/django_historique/1.0',
    license='GPL',
    packages=['django_historique'],
    package_dir={'django_historique': 'django_historique'},
    include_package_data=True,
    zip_safe=True,
    install_requires=['django'],
)
