from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
execfile(os.path.join("zoner", "release.py"))

setup(
    name="zoner",
    version=version,
    
    description=description,
    long_description=long_description,
    author=author,
    author_email=email,
    url=url,
    download_url=download_url,
    license=license,
    
    install_requires = [
        "TurboGears >= 1.0.4, < 1.1.0alpha",
        "SQLAlchemy >= 0.3.10, < 0.5.0alpha",
        "easyzone >= 1.2.0",
        "TGBooleanFormWidget",
        "TGExpandingFormWidget",
        "dnspython",
    ],
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where='zoner',
                                     package='zoner'),
    keywords = [
        'turbogears.app',
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: Name Service (DNS)',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration',
        'Intended Audience :: System Administrators',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Applications',
    ],
    test_suite = 'nose.collector',
    entry_points = {
        'console_scripts': [
            'zoner = zoner.commands:start',
            'zoner_users = zoner.commands:user_manage',
        ],
    },
    data_files = [
        ('config', ['sample-prod.cfg'])
    ],
)
