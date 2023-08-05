import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

import os
execfile(os.path.join("releasemanager","web", "console", "release.py"))

setup(
    name='relman_webconsole',
    version=version,
    description=description,
    author=author,
    author_email=email,
    url=url,
    install_requires=[
        "Pylons>=0.9.4", "releasemanager>=1.01",
        "ToscaWidgets",
    ],
    namespace_packages=['releasemanager.web'],
    packages=find_packages(exclude=['ez_setup']),
    test_suite = 'nose.collector',
    include_package_data = True,
    package_data = {
      'releasemanager.web.console' : ['*.txt', '*.xml'],
    },
    zip_safe = False,
    entry_points="""
    [paste.app_factory]
    main=releasemanager.web.console:make_app
    [paste.app_install]
    main=paste.script.appinstall:Installer
    """,
    keywords = [
        'releasemanager.web',
    ],
)
