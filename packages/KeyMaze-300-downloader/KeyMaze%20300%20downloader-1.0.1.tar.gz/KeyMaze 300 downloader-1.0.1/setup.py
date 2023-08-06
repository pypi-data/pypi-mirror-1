#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
setup(name='KeyMaze 300 downloader',
      version='1.0.1',
      url='http://gitweb.thetys-retz.net/?p=gpsd4;a=summary',
      author='Vincent-Xavier JUMEL',
      author_email='vxjumel@tuxfamilyv.org',
      requires=['serial'],
      packages=['km'],
      data_files=[('/etc/udev/rules.d',['etc/udev/rules.d/99-KeyMaze300.rules']),('/usr/share/km',['usr/share/km/firsttrackpoints.bin','usr/share/km/nexttrackpoints.bin','usr/share/km/waypoints.bin'])],
      license='GPL-3'
      )
