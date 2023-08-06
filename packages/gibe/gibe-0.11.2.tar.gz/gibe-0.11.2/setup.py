from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
execfile(os.path.join("gibe", "release.py"))

setup(
    name="gibe",
    version=version,
    
    # uncomment the following lines if you fill them out in release.py
    description=description,
    long_description=long_description,
    author=author,
    author_email=email,
    url=url,
    download_url=download_url,
    license=license,
    
    install_requires = [
        "TurboGears == 1.0.3.2",
        "SQLAlchemy == 0.3.11", 
        "Genshi >= 0.3.1", 
        "TurboTinyMCE >= 1.0.3",
        "Routes >= 1.5",
        "TurboMail >= 1.0.1",
        "dateutil >= 1.1",
        "Scriptaculous",
    ],
    scripts = ["start-gibe.py"],
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where='gibe',
                                     package='gibe'),
    keywords = [
        # Use keywords if you'll be adding your package to the
        # Python Cheeseshop
        
        # if this has widgets, uncomment the next line
        # 'turbogears.widgets',
        
        # if this has a tg-admin command, uncomment the next line
        # 'turbogears.command',
        
        # if this has identity providers, uncomment the next line
        # 'turbogears.identity.provider',
    
        # If this is a template plugin, uncomment the next line
        # 'python.templating.engines',
        
        # If this is a full application, uncomment the next line
        'turbogears.app',
        'blog',
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: TurboGears',
        # if this is an application that you'll distribute through
        # the Cheeseshop, uncomment the next line
        'Framework :: TurboGears :: Applications',
        
        # if this is a package that includes widgets that you'll distribute
        # through the Cheeseshop, uncomment the next line
        # 'Framework :: TurboGears :: Widgets',
    ],
    test_suite = 'nose.collector',
    entry_points = """
        [gibe.comment_formats]
        tinymce = gibe.tinymcesupport
        postmarkup = gibe.postmarkupsupport

        [turbogears.widgets]
        gibetags = gibe.tags.widgets
        gibebloggingpro = gibe.bloggingprotheme.widgets

        [gibe.plugins]
        gibetags = gibe.tags.plugin:TagsPlugin
        gibebloggingpro = gibe.bloggingprotheme.plugin:BloggingProPlugin
        gibeprettify = gibe.prettify.plugin:PrettifyPlugin

    """,
)
    
