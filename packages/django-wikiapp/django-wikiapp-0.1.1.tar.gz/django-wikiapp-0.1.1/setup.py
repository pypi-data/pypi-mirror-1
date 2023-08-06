from setuptools import setup, find_packages

version = '0.1.1'

setup(
    name='django-wikiapp',
    version=version,
    description=("A simple pluggable wiki application for Django"
                 " with revision and multiple markup support."),
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python",
        "Environment :: Web Environment",
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords='wiki,django',
    author='Eduardo de Oliveira Padoan',
    author_email='eduardo.padoan@gmail.com',
    url='http://launchpad.net/django-wikiapp/',
    license='BSD',
    packages=find_packages(),
    setup_requires=['setuptools_bzr'],
    include_package_data=True,
    zip_safe=False,
)
