from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
execfile(os.path.join("TGIXEDIT", "release.py"))

setup(
    name="TGIXEDIT",
    version=version,

    # uncomment the following lines if you fill them out in release.py
    description=description,
    #long_description=long_description,
    author=author,
    author_email=email,
    url=url,
    download_url=download_url,
    license=license,

    install_requires = ["TurboGears >= 1.0.1"],
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(),
    package_data = find_package_data(where='TGIXEDIT',
                                     package='TGIXEDIT'),
    keywords = [
        'turbogears.widgets',
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: JavaScript',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Widgets',
        'License :: OSI Approved :: BSD License',
    ],
    entry_points = """
    [turbogears.widgets]
    TGIXEDIT = TGIXEDIT.widgets
    """,
    test_suite = 'nose.collector',
    )
