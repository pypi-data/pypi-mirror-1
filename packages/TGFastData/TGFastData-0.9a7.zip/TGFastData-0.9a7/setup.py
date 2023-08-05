from setuptools import setup, find_packages
from pkg_resources import DistributionNotFound

import sys, os

if sys.version_info < (2, 3):
    raise SystemExit("Python 2.3 or later is required")

execfile(os.path.join("tgfastdata", "release.py"))

commands = dict()
if "docs" in sys.argv:
    try:
        from docgen import GenSite
        commands["docs"] = GenSite
    except DistributionNotFound:
        pass

setup(
    name="TGFastData",
    version=version,
    author=author,
    author_email=email,
    download_url=download_url,
    license=license,
    description="Automatic user interface generation for TurboGears",
    long_description="""
FastData generates a user interface based upon model objects in
user projects.""",
    url=url,
    zip_safe=False,
    install_requires = ["TurboGears > 0.9a6"],
    packages=find_packages(),
    include_package_data = True,
    entry_points = """
    [turbogears.extensions]
    fastdata = tgfastdata.plugin
    """,
    
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    test_suite = 'nose.collector',
    )
    
