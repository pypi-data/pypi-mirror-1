from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
from pkg_resources import DistributionNotFound

import sys
import os

if sys.version_info < (2, 4):
    raise SystemExit("Python 2.4 or later is required")

execfile(os.path.join('mopowg', 'release.py'))


# setup params
install_requires = ["docutils >= 0.4",
                    "Pygments >= 0.8.1",
                    "Genshi >= 0.4.2"]

setup(
    name="mopowg",
    version=version,
    author=author,
    author_email=email,
    download_url="http://hg.python.org.tw/mopowg",
    license=license,
    description=description,
    long_description=long_description,
    url="http://hg.python.org.tw/mopowg",
    zip_safe=False,
    install_requires = install_requires,
    packages=find_packages(),
    include_package_data=True,
    package_data = {'docs':['*.html', '*.css'],
                    'apidocs':['*.html', '*.css'],
                    },
    exclude_package_data={"volume1" : ["*"]},
    entry_points = """
    [console_scripts]
    mopowg = mopowg.mopowg:cmdtool
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
