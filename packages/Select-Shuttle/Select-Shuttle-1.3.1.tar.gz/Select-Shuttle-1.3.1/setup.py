from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
execfile(os.path.join("selectshuttle", "release.py"))

setup(
    name="Select-Shuttle",
    version=version,
    
    # uncomment the following lines if you fill them out in release.py
    description=description,
    author=author,
    author_email=email,
    url=url,
    download_url=download_url,
    license=license,
    
    install_requires = ["TurboGears >= 0.9a5dev-r1153"],
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where='selectshuttle',
                                     package='selectshuttle'),
    keywords = [
        'turbogears.widgets',
    ],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Widgets',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    entry_points = """
    [turbogears.widgets]
    selectshuttle = selectshuttle.widgets
    """,
    test_suite = 'nose.collector',
    )

