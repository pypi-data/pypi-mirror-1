#!/usr/bin/env python
import sys
import os
import subprocess
from distutils.spawn import find_executable
from keyring import get_password

class Clipboard(object):

    def _read_win32(self):
        try:
            import win32clipboard as clipboard
            import win32con
        except ImportError:
            return
        clipboard.OpenClipboard()
        try:
            return clipboard.GetClipboardData(win32con.CF_TEXT)
        finally:
            clipboard.CloseClipboard()

    def _read_darwin(self):
        proc = subprocess.Popen('/usr/bin/pbpaste', shell=True,
                                stdout=subprocess.PIPE)
        return proc.stdout.read()

    def _read_linux2(self):
        if os.environ.get('DISPLAY') is not None:
            xsel = find_executable('xsel')
            if xsel is not None:
                return os.popen(xsel).read()
            xclip = find_executable('xclip')
            if xclip is not None:
                return os.popen('%s -o' % xclip).read()

    def read(self):
        meth = '_read_%s' % sys.platform
        if hasattr(self, meth):
            return getattr(self, meth)()
        else:
            return self._read_linux2()

    def _write_process(self, cmd, value):
        proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE)
        proc.stdin.write(value)

    def _write_win32(self, value):
        try:
            import win32clipboard as clipboard
            import win32con
        except ImportError:
            return None

        clipboard.OpenClipboard()
        try:
            clipboard.EmptyClipboard()
            clipboard.SetClipboardText(value)
        finally:
            clipboard.CloseClipboard()

    def _write_darwin(self, value):
        self._write_process('/usr/bin/pbcopy', value)

    def _write_linux2(self, value):
        if os.environ.get('DISPLAY') is not None:
            xsel = find_executable('xsel')
            if xsel is not None:
                self._write_process(xsel, value)
            xclip = find_executable('xclip')
            if xclip is not None:
                self._write_process('%s -i' % xclip, value)

    def write(self, value):
        meth = '_write_%s' % sys.platform
        if hasattr(self, meth):
            getattr(self, meth)(value)
        else:
            # default
            self._write_linux2(value)


def main():
    if len(sys.argv) != 2:
        print('Usage: clvault-get service')
        sys.exit(1)
    service = sys.argv[1]
    res = get_password(service, 'clvault-password')
    if res is None:
        print('No password')
    else:
        if ':::' in res:
            username, password = res.split(':::')
            print('The username is "%s"' % username)
        else:
            password = res
        clip = Clipboard()
        clip.write(password)
        print('The password has been copied in your clipboard')

if __name__ == '__main__':
    main()

