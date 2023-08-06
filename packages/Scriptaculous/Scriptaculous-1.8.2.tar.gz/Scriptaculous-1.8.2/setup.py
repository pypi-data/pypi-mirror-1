from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
execfile(os.path.join("scriptaculous", "release.py"))

setup(
    name="Scriptaculous",
    version=version,

    description=description,
    author=author,
    author_email=email,
    url=url,
    download_url=download_url,
    license=license,

    install_requires = ["TurboGears >= 0.9a2"],
    scripts = [],
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where='scriptaculous',
                                     package='scriptaculous'),
    keywords = [
        'turbogears.widgets',
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: JavaScript',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Widgets',
    ],
    entry_points = """
    [turbogears.widgets]
    scriptaculous = scriptaculous.widgets
    scriptaculous3rd = scriptaculous.thirdparty
    """,
    test_suite = 'nose.collector',
    )
