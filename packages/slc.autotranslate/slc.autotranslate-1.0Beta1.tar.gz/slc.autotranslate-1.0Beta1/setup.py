from setuptools import setup, find_packages
import os

version = '1.0Beta1'

tests_require=[
        'interlude',
        ]

setup(name='slc.autotranslate',
    version=version,
    description="Automatically translate files uploaded by PloneFlashUpload",
    long_description=open("slc/autotranslate/README.txt").read() + "\n" +
                    open(os.path.join("docs", "HISTORY.txt")).read(),
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
