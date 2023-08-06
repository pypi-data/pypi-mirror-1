#!/usr/bin/env python
'''
Created on 18/12/2009
Programa que permite colgar llamadas de un Asterisk
con mas de X tiempo.

@version: 0.0.1
@organization: Sapian SA
@author: Sebastian Rojo
'''
from ez_setup import use_setuptools
from setuptools import setup, find_packages

use_setuptools()
setup(name="AsteriskChannelHangup",
    version="0.0.1.7-README-2",
    description="Programa utilizado para prevenir canales colgados en una planta asterisk",
    author="Sebastian rojo",
    author_email="srojo@sapian.com.co",
    url="http://www.sapian.com.co",
    license="GPL",
    package_data = {'':["conf/*"],'':["html/*"]},
    packages=["AsteriskChannelHangup"],
    scripts=['AsteriskSoftHangupOldChannels.py','ez_setup.py'],
    data_files=[('conf',['conf/py-asterisk.conf.sample'])],
    install_requires = ["py-asterisk"]
)
