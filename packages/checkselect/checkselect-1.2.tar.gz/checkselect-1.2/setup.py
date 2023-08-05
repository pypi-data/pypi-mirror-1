from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
execfile(os.path.join("checkselect", "release.py"))

setup(
    name="checkselect",
    version=version,

    description=description,
    long_description=long_description,
    author=author,
    author_email=email,
    url=url,
    license=license,

    install_requires = ["TurboGears >= 1.0.2dev-r2768"],
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where='checkselect',
                                     package='checkselect'),
    keywords = [
        'turbogears.widgets',
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Widgets',
    ],
    entry_points = """
    [turbogears.widgets]
    checkselect = checkselect.widgets
    """,
    test_suite = 'nose.collector',
    )