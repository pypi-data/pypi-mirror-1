from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(
    name='ProjectName',
    version='0.1',
    #description="",
    #author="",
    #author_email="",
    #url="",
    install_requires=["Pylons>=0.9.5"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite = 'nose.collector',
    package_data={'projectname': ['i18n/*/LC_MESSAGES/*.mo']},
    entry_points="""
    [paste.app_factory]
    main=projectname:make_app
    [paste.app_install]
    main=pylons.util:PylonsInstaller
    """,
)
