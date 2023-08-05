from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
execfile(os.path.join("submodal", "release.py"))

setup(
    name="submodal",
    version=version,
    
    description=description,
    long_description=long_description,
    author=author,
    author_email=email,
    url=url,
    #download_url=download_url,
    license=license,
    
    install_requires = ["TurboGears >= 1.0.2dev-r2597"],
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where='submodal',
                                     package='submodal'),
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
    submodal = submodal.widgets
    """,
    test_suite = 'nose.collector',
    )
