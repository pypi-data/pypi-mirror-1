from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
execfile(os.path.join("TGExtJS", "release.py"))

setup(
    name="TGExtJS",
    version=version,

    # uncomment the following lines if you fill them out in release.py
    description=description,
    #long_description=long_description,
    author=author,
    author_email=email,
    url=url,
    #download_url=download_url,
    license=license,

    install_requires = [
        "TurboGears >= 1.0.1",
        "Scriptaculous",
    ],
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(),
    package_data = find_package_data(where='TGExtJS',
                                     package='TGExtJS'),
    keywords = [
        'turbogears.widgets',
    ],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: JavaScript',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Widgets',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    ],
    entry_points = """
    [turbogears.widgets]
    TGExtJS = TGExtJS.widgets
    """,
    test_suite = 'nose.collector',
    )
