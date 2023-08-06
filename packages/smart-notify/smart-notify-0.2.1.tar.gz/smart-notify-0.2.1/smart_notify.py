#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------#
# smart_notify.py
# Lars Yencken <lljy@csse.unimelb.edu.au>
# vim: ts=4 sw=4 sts=4 et tw=78:
# Tue Apr  8 16:15:50 EST 2008
#
#----------------------------------------------------------------------------#

"Uses either pynotify or Growl to leave a transient note for the user."

import sys, optparse

#----------------------------------------------------------------------------#
# PUBLIC
#----------------------------------------------------------------------------#
 
def notify(title=None, message=None, app_name='python shell'):
    "Provide the user with a notification or fail silently."
    try:
        _use_pynotify(title=title, message=message, app_name=app_name)
        return
    except ImportError:
        pass

    try:
        _use_growl(title=title, message=message, app_name=app_name)
    except ImportError:
        pass

#----------------------------------------------------------------------------#

def _use_pynotify(app_name=None, title=None, message=None):
    import pynotify
    pynotify.init(app_name)
    n = pynotify.Notification(title, message, "dialog-info")
    n.set_urgency(pynotify.URGENCY_NORMAL)
    n.set_timeout(pynotify.EXPIRES_DEFAULT)
    n.show()
    return

#----------------------------------------------------------------------------#

def _use_growl(app_name=None, title=None, message=None):
    import Growl
    n = Growl.GrowlNotifier(applicationName=app_name, notifications=['info'])
    n.register()
    n.notify('info', title, message)
    return

#----------------------------------------------------------------------------#
# PRIVATE
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# MODULE EPILOGUE
#----------------------------------------------------------------------------#

def _createOptionParser():
    usage = \
"""%prog [options] title message

Uses either pynotify or Growl to display a status message to the user for a
few seconds. If neither are available, this script fails silently."""

    parser = optparse.OptionParser(usage)

    parser.add_option('--debug', action='store_true', dest='debug',
            default=False, help='Enables debugging mode [False]')

    return parser

#----------------------------------------------------------------------------#

def main(argv):
    parser = _createOptionParser()
    (options, args) = parser.parse_args(argv)

    try:
        [title, message] = args
    except:
        parser.print_help()
        sys.exit(1)

    notify(title=title, message=message, app_name="Python shell")
    
    return

#----------------------------------------------------------------------------#

if __name__ == '__main__':
    main(sys.argv[1:])

#----------------------------------------------------------------------------#

# vim: ts=4 sw=4 sts=4 et tw=78:
