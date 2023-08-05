from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
execfile(os.path.join("tinymce", "release.py"))

setup(
    name="TurboTinyMCE",
    version=version,
    
    description=description,
    author=author,
    author_email=email,
    url=url,
    download_url=download_url,
    license=license,
    
    install_requires = ["TurboGears >= 0.9a4"],
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where='tinymce', package='tinymce'),
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
    tinymce = tinymce.widgets
    """,
    test_suite = 'nose.collector',
    )
    
