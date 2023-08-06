from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
from ConfigParser import SafeConfigParser
config_file = 'setup.cfg'
cfg = SafeConfigParser()
if not os.path.exists(config_file):
    raise IOError('File not found : %s' % config_file)

cfg.read(config_file)

NAME = cfg.get('metadata', 'name')

setup(
    name=NAME,
    version=cfg.get('metadata', 'version'),
    
    description=cfg.get('metadata', 'description'),
    author=cfg.get('metadata', 'author'),
    author_email=cfg.get('metadata', 'author_email'),
    url=cfg.get('metadata', 'url'),
    download_url=cfg.get('metadata', 'download_url'),
    license=cfg.get('metadata', 'license'),
    
    install_requires = ["TurboGears >= 0.9a2"],
    scripts = [],
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where=cfg.get('metadata', 'name'),
                                     package=cfg.get('metadata', 'name')),
    keywords = [
        # Use keywords if you'll be adding your package to the
        # Python Cheeseshop
        'turbogears.widgets',
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
        'Framework :: TurboGears :: Widgets',
    ],
    entry_points = """
    [turbogears.widgets]
    %(name)s = %(name)s.widgets
    """ % dict(name=NAME),
    test_suite = 'nose.collector',
    )
    
