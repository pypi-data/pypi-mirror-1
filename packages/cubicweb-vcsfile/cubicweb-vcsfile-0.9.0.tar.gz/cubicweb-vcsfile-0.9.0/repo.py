"""repository abstraction for supported repositories

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from os.path import exists
from logging import getLogger

from yams import ValidationError
from logilab.common.modutils import LazyObject

from cubicweb import set_log_methods

VCS_REPOS = {'subversion': LazyObject('cubes.vcsfile.reposvn', 'SVNRepository'),
             'mercurial': LazyObject('cubes.vcsfile.repohg', 'HGRepository'),
             }


class VCSException(Exception):
    def __init__(self, repoeid, attr, msgid, msgargs):
        self.repoeid = repoeid
        self.attr = attr
        self.msgid = msgid
        self.msgargs = msgargs

    def __str__(self):
        return '%s.%s: %s' % (self.repoeid, self.attr,
                              self.msgid % self.msgargs)

    def to_validation_error(self, translate):
        msg = translate(self.msgid) % self.msgargs
        return ValidationError(self.repoeid, {self.attr: msg})


class VCSRepository(object):
    type = None # to set in concret classes

    def __init__(self, eid, path, encoding):
        # eid of the associate Repository entity
        self.eid = eid
        # encoding of files, messages... Normalize for later comparison
        self.encoding = encoding.lower()
        # path to the repository
        if isinstance(path, unicode):
            fspath = path.encode(encoding)
        else:
            fspath = path
        if not exists(fspath):
            msg = _('%s does not exist on the file system')
            raise VCSException(eid, 'path', msg, path)
        try:
            fspath = self.canonicalize(fspath)
        except:
            self.exception('invalid repository')
            msg = _('%s is not a valid %s repository')
            raise VCSException(eid, 'path', msg, (path, self.type))
        self.path = fspath

    def __str__(self):
        return '%s:%s' % (self.type, self.path)

    def encode(self, ustring):
        if ustring:
            return ustring.encode(self.encoding)
        return ''

    def decode(self, string):
        if string:
            return string.decode(self.encoding)
        return u''

    def canonicalize(self, path):
        return path

    def import_content(self, source, repoentity):
        """import content from the repository

        NOTE: server side only method
        """
        raise NotImplementedError()

    def file_content(self, path, rev):
        """extract a binary stream with the content of the file at `path` at
        revision `rev` in the repository
        """
        raise NotImplementedError()

    def revision_transaction(self, session, entity):
        """open a transaction to create a new revision corresponding to the
        given entity
        """
        raise NotImplementedError()

    def add_versioned_file_content(self, session, transaction, vf, entity,
                                   data):
        """add a new revision of a versioned file"""
        raise NotImplementedError()

    def add_versioned_file_deleted_content(self, session, transaction, vf,
                                           entity):
        """add a new revision of a just deleted versioned file"""
        raise NotImplementedError()

set_log_methods(VCSRepository, getLogger('cubicweb.vcs'))
