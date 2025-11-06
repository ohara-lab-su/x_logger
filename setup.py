#!/usr/bin/env python

# Copyright (C) 2014,2015 K.NAKADA

__author__ = "Kengo NAKADA"
__maintainer__ = "Kengo NAKADA"
__credits__ = ["Kengo NAKADA"]
__email__ = "kengo.nakada@gmail.com"
# __email__ = "kengo.nakada@spring8.or.jp"
__copyright__ = "Copyright 2014-2018 Kengo NAKADA"
__license__ = "Apache2"
__status__ = "alpha"

# __version__    = "0.0.1"
# __license__    = "MIT"

from setuptools import setup, find_packages
import glob
import re

def get_version_from_toml(toml_path):
    """
    Python 3.6 向け: TOML ファイルから version 番号を正規表現で抽出。
    [project] セクション内でも対応。
    """
    with open(toml_path, encoding="utf-8") as f:
        text = f.read()
    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', text)
    if not match:
        raise RuntimeError("TOML ファイル内に version が見つかりません。")
    return match.group(1)

__version__ = get_version_from_toml("pyproject.toml")

long_description = "x_logger"

# if os.path.exists('README.md'):
#    long_description = open('README.md').read()

package_src_dir = "x_logger"
print("*****************************************")
packages = find_packages()
print(packages)
print("*****************************************")

setup(
    name="x_logger",
    # packages=find_packages(),
    packages=packages,
    #       package_dir  = {'':'StructureAnalysisEnvironment'},
    #       include_package_data=True,
    #       package_data = { '': ['LICENSE.txt', 'README.md']},
    # data_files=[(package_src_dir, files)],
    # scripts=script,
    version=__version__,
    description="XLogger",
    long_description=long_description,
    author="K.NAKADA",
    #       author_email = ['kengo.nakada@gmail.com','kengo.nakada@spring8.or.jp'],
    #       author_email = 'kengo.nakada@gmail.com',
    # author_email='kengo.nakada@spring8.or.jp',
    author_email="kengo.nakada@gmail.com",
    license="Apache2.0",
    install_requires=[],
    #       platforms = ['linux','OSX','Window'],
    #       classifiers = [
    #           'Programming Language :: Python :: 2.7',
    #           'Intended Audience :: Science/Research',
    #           'License :: OSI Approved :: MIT License'
    #           ]
)
