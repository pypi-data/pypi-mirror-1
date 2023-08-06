# Copyright (C) 2008 Marco Pantaleoni. All rights reserved
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# VERSION = (major, minor, release-tag)
#
# Remember that for setuptools the release-tag can have special meaning:
#   words alphabetically before 'final' are pre-release tags, otherwise
#   are post-release tags, *BUT*
#   'pre', 'preview' and 'rc' prefixes are considered equivalend to 'c'
#
#    http://peak.telecommunity.com/DevCenter/setuptools#specifying-your-project-s-version
#
VERSION = (1, 0, 'dev')

def get_bzr_info(path = None):
    try:
        from bzrlib.branch import Branch
        from bzrlib.errors import NotBranchError
        from bzrlib.plugin import load_plugins
    except ImportError:
        Branch = None
        return None

    import os

    if path is None:
        path = __file__
    revno = None

    try:
        branch, inpath = Branch.open_containing(path)
        revno = branch.revno()
        revinfo = branch.last_revision_info()
        (rno, revname) = revinfo

        basepath = branch.base
        if basepath.startswith('file://'):
            basepath = basepath[7:]

        return dict(revno     = revno,
                    revinfo  = revinfo,
                    revname  = revname,
                    basepath = basepath,
                    inpath   = inpath)
    except NotBranchError:
        return None
    return None

def get_bzr_info_cached(path = None):
    import os
    if path is None:
        path = __file__

    info = get_bzr_info(path)
    if info is not None:
        import os
        #print "from bzr %s %s" % (info['revno'], info['revname'])
        #cr_dirname = info['basepath']
        cr_dirname = os.path.dirname(__file__)
        #print "CR_DIRNAME: %s" % cr_dirname
        cr_path = os.path.join(cr_dirname, 'bzrcachedrev.py')
        fh = open(cr_path, 'w')
        fh.write('info    = %r\n' % info)
        fh.write('revno   = %r\n' % info['revno'])
        fh.write('revname = %r\n' % info['revname'])
        fh.write('revinfo = (%r, %r)\n' % info['revinfo'])
        fh.close()
        return info

    try:
        from bzrcachedrev import info
        #print "from cache %s %s" % (info['revno'], info['revname'])
        return info
    except ImportError:
        pass
    return None

def get_bzr_revno(path = None):
    info = get_bzr_info_cached(path)
    if info is None:
        return info
    return info['revno']

def get_bzr_revision(path = None):
    info = get_bzr_info_cached(path)
    if info is not None:
        revno   = info['revno']
        revname = info['revname']
        return u'BZR-r%s-%s' % (revno, revname)
    revno = get_bzr_revno(path)
    if revno:
        return u'BZR-r%s' % revno
    return u'BZR-unknown'

def get_version():
    "Returns the version as a human-format string."
    v = '.'.join([str(i) for i in VERSION[:-1]])
    if VERSION[-1]:
        v = '%s-%s-%s' % (v, VERSION[-1], get_bzr_revision())
    return v

def get_version_setuptools():
    """
    Returns the version as a human-format string suitable for setuptools.
    For more info, see:

    http://peak.telecommunity.com/DevCenter/setuptools#specifying-your-project-s-version
    """
    version_tuple = VERSION
    if version_tuple[2] is not None:
        rtag = version_tuple[2]
        version = "%d.%d%s" % version_tuple
        if rtag.startswith('dev'):
            bzr_rev = get_bzr_revision()
            if bzr_rev:
                version += "-%s" % bzr_rev
    else:
        version = "%d.%d" % version_tuple[:2]
    return version
