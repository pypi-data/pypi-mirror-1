# -*- coding: utf-8 -*-
#
# Copyright (C) 2008 OpenSourceXpress Ltd. (http://www.ossxp.com)
# Author: Jiang Xin
# Contact: http://www.ossxp.com
#          http://www.worldhello.net
#          http://moinmo.in/JiangXin
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='pySvnManager',
    version="0.2.2",
    description='SVN authz web management tools.',
    author='Jiang Xin',
    author_email='jiangxin@ossxp.com',
    url='https://sourceforge.net/projects/pysvnmanager',
    #install_requires=["Pylons>=0.9.6.2", "docutils", "python-ldap"],
    install_requires=[
        "Pylons==0.9.6.2",
        "docutils",
        "Babel",
        "Mako==0.1.8",
        "WebHelpers==0.3.2",
        "Routes==1.7.3",
        "Beaker>=0.8.1",
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'pysvnmanager': ['i18n/*/LC_MESSAGES/*.mo', 'config/*.in', ]},
    message_extractors = {'pysvnmanager': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('public/**', 'ignore', None)]},
    entry_points="""
    [paste.app_factory]
    main = pysvnmanager.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
    zip_safe = False,
)
