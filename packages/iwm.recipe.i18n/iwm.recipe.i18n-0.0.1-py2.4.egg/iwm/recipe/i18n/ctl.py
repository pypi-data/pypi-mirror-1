
import os
import sys
import getopt

import i18nmergeall


def main_i18nmergeall():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'l:h',
            ['help', 'locals-dir='])
    except getopt.error, msg:
        i18nmergeall.usage(1, msg)

    path = None
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            i18nmergeall.usage(0)
        elif opt in ('-l', '--locales-dir'):
            cwd = os.getcwd()
            # This is for symlinks. Thanks to Fred for this trick.
            if os.environ.has_key('PWD'):
                cwd = os.environ['PWD']
            path = os.path.normpath(os.path.join(cwd, arg))

    if path is None:
        i18nmergeall.usage(1, 'You must specify the path to the locales directory.')
    i18nmergeall.main(path)