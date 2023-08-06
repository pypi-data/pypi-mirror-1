from setuptools import setup, find_packages
import os

version = '0.3b1'

tests_require=[
            'zope.testing',
            'plone.app.blob',
            ]

setup(
    name='slc.dublettefinder',
    version=version,
    description=\
    "The goal of syslab.dublettefinder is to find duplicate files "
    "(dublettes ;) in the ZODB and then warn the user via validation "
    "error during content edit/creation.",
    long_description=open("README.txt").read() + "\n" +
                    open(os.path.join("docs", "HISTORY.txt")).read(),
    classifiers=[
    "Framework :: Plone",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    ],
    keywords='dublettefinder dublette duplications',
    author='JC Brand, Syslab.com GmbH',
    author_email='brand@syslab.com',
    url='http://plone.org/products/slc.dublettefinder/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['slc'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'archetypes.schemaextender',
    ],
    tests_require=tests_require,
    extras_require=dict(tests=tests_require),
    entry_points="""
        [z3c.autoinclude.plugin]
        target = plone
        """,
    )
