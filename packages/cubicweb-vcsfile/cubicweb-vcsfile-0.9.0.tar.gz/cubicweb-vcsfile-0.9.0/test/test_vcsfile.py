"template automatic tests"
import os
from logilab.common.testlib import unittest_main
from cubicweb.devtools import BaseApptestConfiguration, testlib

class MyConfig(BaseApptestConfiguration):
    sourcefile = 'sources'

class AutomaticWebTest(testlib.AutomaticWebTest):
    configcls = MyConfig
    no_auto_populate = ('Repository', 'Revision', 'VersionedFile',
                        'VersionContent', 'DeletedVersionContent',)
    ignored_relations = ('at_revision', 'parent_revision',
                         'from_repository', 'from_revision', 'content_for',)

    def custom_populate(self, how_many, cursor):
        self.repo = self.add_entity('Repository', type=u'mercurial',
                                    path=u'testrepohg', encoding=u'latin1')
        self.commit()
        self.source = self.env.repo.sources[-1]
        if not os.path.exists(self.source.dbpath):
            self.env.repo._type_source_cache = {}
            self.env.repo._extid_cache = {}
            self.source._need_sql_create = True
            self.source._need_full_import = True
            self.source.set_schema(self.env.repo.schema)
        self.source.init()

    def tearDown(self):
        super(AutomaticWebTest, self).tearDown()
        try:
            os.remove(self.source.dbpath)
        except:
            pass

if __name__ == '__main__':
    unittest_main()
