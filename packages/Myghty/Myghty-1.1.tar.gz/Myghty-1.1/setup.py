from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name = "Myghty",
    version = "1.1",
    description = "View/Controller Framework and Templating Engine",
    author = "Mike Bayer",
    author_email = "mike@myghty.org",
    url = "http://www.myghty.org",
    download_url = "http://www.myghty.org/links.myt?linkid=download",
    package_dir = {'':'lib'},
    packages = find_packages('lib'),
    license = "MIT License",
    long_description = """\
A Python-based template and view-controller framework derived from HTML::Mason. Supports the full featureset of Mason, allowing component-based web development with Python-embedded HTML, and includes many new concepts and features not found in Mason.

`Development SVN <http://svn.myghty.org/myghty/trunk#egg=myghty-dev>`_

""",
    classifiers = ["Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    "Topic :: Text Processing :: Markup"
    ],
    package_data={
            'myghty': [
                'paster_templates/*/*.py', 
                'paster_templates/*/*_tmpl', 
                'paster_templates/*/+package+/*.py', 
                'paster_templates/*/+package+/*.my?', 
                'paster_templates/*/+package+/*_tmpl', 
                'paster_templates/*/+package+/*/*.py', 
                'paster_templates/*/+package+/*/*.my?', 
                'paster_templates/*/+package+/*/*_tmpl', 
                'paster_templates/*/+package+/*/*.css', 
                'paster_templates/*/+package+/*/*.png', 
                'paster_templates/*/+package+/*/*handler', 
                ],
    },
    install_requires=["Routes >= 1.0", "Paste", "PasteDeploy", "PasteScript"],

    entry_points="""
    [paste.paster_create_template]
    myghty_routes=myghty.paste.templates:RoutesTemplate
    myghty_simple=myghty.paste.templates:SimpleTemplate
    myghty_modulecomponents=myghty.paste.templates:MCTemplate
    """,
    )


