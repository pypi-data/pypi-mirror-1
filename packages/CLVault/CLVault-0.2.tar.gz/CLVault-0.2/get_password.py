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

    def _read_posix(self):
        if os.environ.get('DISPLAY') is not None:
            xsel = find_executable('xsel')
            if xsel is not None:
                return os.popen(xsel).read()
            xclip = find_executable('xclip')
            if xclip is not None:
                return os.popen('%s -o' % xclip).read()

    def read(self):
        return getattr(self, '_read_%s' % sys.platform)()

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

    def _write_posix(self, value):
        if os.environ.get('DISPLAY') is not None:
            xsel = find_executable('xsel')
            if xsel is not None:
                self._write_process(xsel, value)
            xclip = find_executable('xclip')
            if xclip is not None:
                self._write_process('%s -i' % xclip, value)

    def write(self, value):
        getattr(self, '_write_%s' % sys.platform)(value)


def main(service):
    res = get_password(service, 'tarek')
    if res is None:
        print('No password')
    else:
        clip = Clipboard()
        clip.write(res)
        print('The password has been copied in your clipboard')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: %s service' % sys.executable)
        sys.exit(1)
    main(sys.argv[1])

