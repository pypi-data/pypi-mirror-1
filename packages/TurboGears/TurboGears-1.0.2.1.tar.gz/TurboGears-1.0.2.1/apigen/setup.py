from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
from pkg_resources import DistributionNotFound

import sys, os

if sys.version_info < (2, 4):
    raise SystemExit("Python 2.4 or later is required")

execfile(os.path.join("apigen", "release.py"))

setup(
    name="apigen",
    version=version,
    author=author,
    author_email=email,
    download_url="http://www.turbogears.org/download/",
    license=license,
    description="Packaged up PythonDoc for easy API generation",
    long_description="""
Easily generate decent looking API docs.""",
    url="http://www.turbogears.org",
    zip_safe=False,
    install_requires = [],
    packages=find_packages(),
    include_package_data=True,
    exclude_package_data={},
    entry_points = """
    [console_scripts]
    apigen = apigen.command:main
    """,
    extras_require = {
    },
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    test_suite = 'nose.collector',
    )
    
