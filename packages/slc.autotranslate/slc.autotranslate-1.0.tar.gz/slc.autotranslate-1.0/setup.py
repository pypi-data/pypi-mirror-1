from setuptools import setup, find_packages
import os

version = '1.0'

tests_require=[
        'interlude',
        ]

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='slc.autotranslate',
    version=version,
    description="Automatically translate files uploaded by PloneFlashUpload",
    long_description = (
        read('README.txt')
        + '\n' +
        read("slc", "autotranslate", "README.txt")
        + '\n' +
        'Change history\n'
        '**************\n'
        + '\n' +
        read("docs", "HISTORY.txt")
        + '\n' +
        'Contributors\n'
        '************\n'
        + '\n' +
        read('CONTRIBUTORS.txt')
        + '\n' 
        ),

    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='plone zope PloneFlashUpload LinguagePlone translate pdf upload slc syslab',
    author='JC Brand',
    author_email='brand@syslab.com',
    url='http://plone.org/products/slc.autotranslate',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['slc'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'Products.LinguaPlone',
        'Products.PloneFlashUpload',
    ],
    tests_require=tests_require,
    extras_require=dict(tests=tests_require),
    entry_points="""
    # -*- Entry points: -*-
    """,
    )
