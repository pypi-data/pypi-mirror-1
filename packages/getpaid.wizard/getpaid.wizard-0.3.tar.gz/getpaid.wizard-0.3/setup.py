import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name="getpaid.wizard",
    version="0.3",
    install_requires=['setuptools',
                      'getpaid.core',], 
    dependency_links=['http://download.zope.org/distribution/',],
    packages=find_packages('src', exclude=["*.tests", "*.ftests"]),
    package_dir= {'':'src'},
    namespace_packages=['getpaid'],
    package_data = {
    '': ['*.txt', '*.zcml', '*.pt'],
    },
    zip_safe=False,
    author='Kapil Thangavelu',
    author_email='kapil.foss@gmail.com',
    description="""Sequence composition of views, viewlets, forms.""",
    license='X11',
    keywords="zope zope3",
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Framework :: Zope3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries",
    ],
    long_description = (
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        'Download\n'
        '**********************\n'
        ),
    )
