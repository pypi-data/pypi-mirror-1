# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------#
# setup.py
# Lars Yencken <lars.yencken@gmail.com>
# vim: ts=4 sw=4 sts=4 et tw=78:
# Tue Apr  8 16:35:12 2008
#
#----------------------------------------------------------------------------#

"Setup script for smart_notify module."

#----------------------------------------------------------------------------#

import os
from distutils.core import setup

#----------------------------------------------------------------------------#

VERSION = '0.2.2'

setup(
        name='smart-notify',
        version=VERSION,
        author='Lars Yencken',
        author_email='lljy@csse.unimelb.edu.au',
        url='http://bitbucket.org/lars512/smart-notify/',
        description='A cross-platform notifier module based on Growl or gnotify.',
        long_description=\
'A cross-platofrm notifier module designed to make use of Growl or gnotify, whichever is available. In the event that neither is, smart-notify fails silently by design.',
        py_modules=['smart_notify'],
        scripts=['smart_notify.py'],
    )
