#!/usr/bin/python
#
# bzr-file-info.py: Get version info for a file from Bazaar VCS.
# Copyright (C) 2008 Alexander Belchenko
#  based on the code from plugin 'file-revno' by Robert Widhopf-Fenk
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

## @file bzr-file-info.py
# Get version info for a file from Bazaar VCS.


if __name__ == '__main__':
    import os, sys, time

    if len(sys.argv) != 2:
        print 'Usage: bzr-file-info.py filename'
        sys.exit(2)

    if sys.platform == 'win32':
        # support for standalone bzr.exe
        import _winreg
        hkey = None
        try:
            hkey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                r'SOFTWARE\Bazaar')
            try:
                path_u, type_ = _winreg.QueryValueEx(hkey, 'BzrlibPath')
            except WindowsError:
                pass
            else:
                parent = os.path.dirname(path_u)
                if not parent in sys.path:
                    sys.path.append(parent)
        except EnvironmentError:
            pass
        if hkey is not None:
            _winreg.CloseKey(hkey)

    try:
        import bzrlib
        from bzrlib import errors
        #import bzrlib.plugin
        #bzrlib.plugin.load_plugins()
        from bzrlib.workingtree import WorkingTree
    except ImportError:
        print '-'
        sys.exit(1)

    def run(filename):
        try:
            tree, relpath = WorkingTree.open_containing(filename)
        except (errors.NotBranchError, errors.NoWorkingTree,
            errors.NoRepositoryPresent), e:
            print >>sys.stderr, str(e)
            print '-'
            return
        branch = tree.branch
        tree.lock_read()
        try:
            file_id = tree.path2id(relpath)
            if file_id is None:
                return
            rtree = tree.basis_tree()
        finally:
            tree.unlock()

        rtree.lock_read()
        try:
            branch.lock_read()
            try:
                try:
                    rev_id = rtree.inventory[file_id].revision
                except errors.NoSuchId, e:
                    print '-'
                    return
                id_to_revno = branch.get_revision_id_to_revno_map()
                print '#%s' % ".".join([str(n) for n in id_to_revno[rev_id]]),
                revision = branch.repository.get_revision(rev_id)
                print time.strftime('%Y/%m/%d', time.localtime(revision.timestamp)),
                print '{%s}' % rev_id
            finally:
                branch.unlock()
        finally:
            rtree.unlock()

    run(sys.argv[1])
