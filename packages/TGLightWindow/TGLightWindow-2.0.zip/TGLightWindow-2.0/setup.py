from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
execfile(os.path.join("TGLightWindow", "release.py"))

setup(
    name="TGLightWindow",
    version=version,

    # uncomment the following lines if you fill them out in release.py
    description=description,
    #long_description=long_description,
    author=author,
    author_email=email,
    url=url,
    download_url=download_url,
    license=license,

    install_requires = [
        "TurboGears >= 1.0.1",
        "Scriptaculous",
    ],
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(),
    package_data = find_package_data(where='TGLightWindow',
                                     package='TGLightWindow'),
    keywords = [
        'turbogears.widgets',
    ],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: JavaScript',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Widgets',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points = """
    [turbogears.widgets]
    TGLightWindow = TGLightWindow.widgets
    """,
    test_suite = 'nose.collector',
    )
