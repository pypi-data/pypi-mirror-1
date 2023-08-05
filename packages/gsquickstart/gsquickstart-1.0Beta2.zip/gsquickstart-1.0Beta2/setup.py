from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
execfile(os.path.join("gsquickstart", "release.py"))

setup(
    name="gsquickstart",
    version=version,

    # uncomment the following lines if you fill them out in release.py
    description=description,
    long_description=long_description,
    author=author,
    author_email=email,
    url=url,
    download_url=download_url,
    license=license,

    install_requires = ["TurboGears >= 1.0", "genshi >= 0.3.6"],
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where='gsquickstart',
                                     package='gsquickstart'),
    keywords = [
        'turbogears.quickstart.template',
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
    ],
    entry_points = """
    [paste.paster_create_template]
    tggenshi = gsquickstart.template:GenshiTemplate
    """,
    #test_suite = 'nose.collector',
    )

