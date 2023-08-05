from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
execfile(os.path.join("file_fields", "release.py"))

setup(
    name="FileFields",
    version=version,
    
    # uncomment the following lines if you fill them out in release.py
    description=description,
    long_description=long_description, 
    author=author,
    author_email=email,
    #url=url,
    #download_url=download_url,
    license=license,
    
    install_requires = ["TurboGears >= 1.0b1", "PIL >= 1.1.5"],
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where='file_fields',
                                     package='file_fields'),
    keywords = ['turbogears.widgets'],
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
    file_fields = file_fields.widgets
    
    [turbogears.extensions]
    file_server = file_fields
    """,
    test_suite = 'nose.collector',
    )
    
