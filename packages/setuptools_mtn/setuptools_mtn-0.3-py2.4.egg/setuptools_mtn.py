# setuptools_mtn -- setuptools support to discover files kept in Monotone
# Copyright (C) 2007 Dale Sedivec

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import popen2
import os
import distutils.log

class Monotone (object):
    def __init__(self, command, capture_stderr=False):
        if capture_stderr:
            popen_constructor = popen2.Popen4
        else:
            popen_constructor = popen2.Popen3
        mtn_executable = os.environ.get("MTN", "mtn")
        popen = self._popen = popen_constructor("%s --xargs -"
                                                % (mtn_executable,))
        popen.tochild.write(command)
        popen.tochild.close()
        self.readline = popen.fromchild.readline
        self._closed = False

    def __iter__(self):
        return iter(self._popen.fromchild)

    def iter_inventory(self):
        "Yields valid file names from 'automate inventory' output."
        for line in self:
            # The specs for this are in monotone's automate.cc.  Briefly:
            #
            #   * First column is " " for unchanged, "D"eleted, or
            #     "R"enamed from
            #   * Second column is " " for unchanged, "R"enamed to, or
            #     "A"dded
            #   * Third column is " " for unchanged, "P"atched, "U"nknown,
            #     "I"gnored, or "M"issing (from the filesystem)
            #
            # Then a space, two ID numbers separated by a space,
            # another space, and the file name.  So we strip the first
            # columns, split on space twice, and return the tail end
            # of the line which should be path/file.
            line = line.rstrip()
            if line[0] == " " and line[2] in " P":
                yield line[4:].split(" ", 2)[2]

    def discard_output(self):
        for line in self:
            pass

    def _close(self):
        assert not self._closed
        self._popen.fromchild.close()
        result = self._popen.wait()
        if os.WIFEXITED(result):
            self.exit_status = (True, os.WEXITSTATUS(result))
        else:
            self.exit_status = (False, result)
        self._closed = True
        return self.exit_status

    def exited_normally(self):
        if not self._closed:
            self._close()
        exited, code = self.exit_status
        return exited and code == 0

def acceptable_mtn_version():
    mtn = Monotone("automate interface_version", capture_stderr=True)
    version = mtn.readline().strip()
    if not mtn.exited_normally():
        return False
    try:
        major, minor = version.split(".", 1)
        if 1 <= int(major) <= 4:
            return True
        else:
            distutils.log.warn("no support for mtn automate version %r"
                               % (version,))
            return False
    except:
        distutils.log.warn("couldn't parse mtn automate version %r"
                           % (version,))
        return False

def find_mtn_root(a_path):
    assert os.path.isabs(a_path)
    assert a_path == os.path.normpath(a_path)
    if os.path.isdir(os.path.join(a_path, "_MTN")):
        return a_path
    else:
        head, tail = os.path.split(a_path)
        if head != a_path:
            return find_mtn_root(head)
        else:
            return None

def get_path_relative_to_mtn_root(mtn_root, abs_path):
    common_path = os.path.commonprefix([mtn_root, abs_path])
    return abs_path[len(common_path) + 1:]

def call_with_cwd(temp_cwd, callable, *args, **kwargs):
    orig_cwd = os.getcwd()
    try:
        try:
            os.chdir(temp_cwd)
        except OSError, e:
            distutils.log.warn("error with mtn plug-in: %s" % (str(e),))
            return None
        return callable(*args, **kwargs)
    finally:
        os.chdir(orig_cwd)

def find_files_in_mtn(a_path):
    abs_path = os.path.normpath(os.path.abspath(a_path))
    mtn_root = find_mtn_root(abs_path)
    if mtn_root is None or not acceptable_mtn_version():
        return
    mtn_relative_path = get_path_relative_to_mtn_root(mtn_root, abs_path)
    if mtn_relative_path:
        strip_before = len(mtn_relative_path) + 1
    else:
        strip_before = 0
    mtn = call_with_cwd(abs_path, Monotone, "automate inventory")
    if not mtn:
        return
    for file in mtn.iter_inventory():
        if (file.startswith(mtn_relative_path)
            and file.rstrip("/") != mtn_relative_path):
            yield os.path.join(a_path, file[strip_before:])
    if not mtn.exited_normally():
        distutils.log.warn("error running mtn: exited=%r status=%r"
                           % mtn.exit_status)

if __name__ == "__main__":
    import sys
    assert len(sys.argv) <= 2, "only an optional path argument can be given"
    if len(sys.argv) == 2:
        a_path = sys.argv[1]
    else:
        a_path = ""
    for name in find_files_in_mtn(a_path):
        print name

__all__ = ["find_files_in_mtn"]
