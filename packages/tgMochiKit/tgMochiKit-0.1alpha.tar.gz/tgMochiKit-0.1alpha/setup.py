from setuptools import setup, find_packages
#from turbogears.finddata import find_package_data

import os
execfile(os.path.join("tgmochikit", "release.py"))

setup(
    name="tgMochiKit",
    version=version,
    
    description=description,
    author=author,
    author_email=email,
    url=url,
    download_url=download_url,
    license=license,
    
    install_requires = [],
    scripts = [],
    zip_safe=False,
    packages=find_packages(),
    include_package_data = True,
    keywords = [
        # Use keywords if you'll be adding your package to the
        # Python Cheeseshop
        
        # if this has widgets, uncomment the next line
        'turbogears.widgets',    
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        # if this is a package that includes widgets that you'll distribute
        # through the Cheeseshop, uncomment the next line
        'Framework :: TurboGears :: Widgets',
    ],
    entry_points = """
    [turbogears.widgets]
    tgmochikit = tgmochikit.widgets
    """,
    test_suite = 'nose.collector',
    )
    
