from setuptools import setup, find_packages
from finddata import find_package_data

import os
execfile(os.path.join("tgext/ws", "release.py"))

setup(
    name="TGWebServices",
    version=version,
    
    description=description,
    long_description=long_description,
    author=author,
    author_email=email,
    url=url,
    license=license,
    
    install_requires = [
        "TurboGears2 >= 2.0",
        "Genshi >= 0.3.4",
        "PEAK-Rules >= 0.5a1.dev-r2555",
    ],
    scripts = [],
    zip_safe=False,
    packages=find_packages(),
    namespace_packages=['tgext'],
    package_data = find_package_data(where='tgext/ws',
                                     package='tgext.ws'),
    keywords = [
        "turbogears.extension"
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        # if this is an application that you'll distribute through
        # the Cheeseshop, uncomment the next line
        # 'Framework :: TurboGears :: Applications',
        
        # if this is a package that includes widgets that you'll distribute
        # through the Cheeseshop, uncomment the next line
        # 'Framework :: TurboGears :: Widgets',
    ],
    test_suite = 'nose.collector'
    )
    
