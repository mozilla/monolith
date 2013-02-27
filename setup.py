""" Setup file.
"""
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'colander',
    'cornice',
    'PasteScript',
    'pyelasticsearch',
    'waitress',
]

test_requires = requires + [
    'coverage',
    'nose',
    'mock',
    'unittest2',
    'Webtest',
]

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()


setup(name='monolith.web',
    version='0.1',
    description='Mozilla Monolith Web Service',
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
    ],
    keywords="web services",
    author='Mozilla Services',
    author_email='services-dev@mozilla.org',
    url='https://github.com/mozilla/monolith',
    packages=find_packages(),
    namespace_packages=['monolith'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=test_requires,
    test_suite="monolith.web",
    extras_require={'test': test_requires},
    entry_points="""\
    [paste.app_factory]
    main = monolith.web:main
    """,
)
