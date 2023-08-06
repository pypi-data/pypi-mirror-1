# -*- coding: UTF-8 -*-
import os

from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

execfile(os.path.join("turbofeeds", "release.py"))

setup(
    name=name,
    version=version,

    description=description,
    long_description=long_description,
    author=author,
    author_email=author_email,
    maintainer=maintainer,
    maintainer_email=maintainer_email,
    url=url,
    download_url=download_url,
    license=license,

    install_requires = [
        "TurboGears >= 1.0"
    ],
    extras_require = {
        "kid": ["TurboKid"]
    },
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where='turbofeeds', package='turbofeeds'),
    keywords = [
        'turbogears.widgets',
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Widgets',
    ],
    entry_points = """
        [turbogears.widgets]
        turbofeeds = turbofeeds.widgets
    """,
    test_suite = 'nose.collector',
)
