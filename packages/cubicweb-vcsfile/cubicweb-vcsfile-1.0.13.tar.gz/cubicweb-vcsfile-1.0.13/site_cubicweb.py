# register VERSION_DATA stored procedure #######################################

from rql.utils import register_function, FunctionDescr

class version_data(FunctionDescr):
    supported_backends = ('postgres', 'sqlite',)
    rtype = 'Bytes'

try:
    register_function(version_data)
except AssertionError:
    pass


# repository specific stuff ####################################################

try:
    from cubicweb.server import SQL_CONNECT_HOOKS
except ImportError: # no server installation
    pass
else:

    options = (
        ('check-revision-interval',
         {'type' : 'int',
          'default': 5*60,
          'help': 'interval between checking of new revisions in repositories \
(default to 5 minutes).',
          'inputlevel': 2,
          'group': 'vcsfile',
          }),
        ('check-revision-commmit-every',
         {'type' : 'int',
          'default': 1,
          'help': 'after how much new imported revisions the transaction \
should be commited (default to 1, e.g. on each revision).',
          'inputlevel': 2,
          'group': 'vcsfile',
          }),
        )


    # VERSION_DATA stored procedure support w/ sqlite ##########################

    def init_sqlite_connection(cnx):
        from cubes.vcsfile import bridge
        def version_data(vceid, cnx=cnx, bridge=bridge):
            try:
                cu = cnx.cursor()
                cu.execute('SELECT REV.cw_revision, REV.cw_from_repository,'
                           ' VF.cw_directory, VF.cw_name '
                           'FROM cw_VersionContent as VC,'
                           ' cw_VersionedFile as VF, cw_Revision as REV '
                           'WHERE VC.cw_eid=%(eid)s AND'
                           ' VC.cw_content_for=VF.cw_eid AND'
                           ' VC.cw_from_revision=REV.cw_eid', {'eid': vceid})
                rev, repoeid, directory, fname = cu.fetchone()
                repohdlr = bridge.repository_handler(repoeid)
                return buffer(repohdlr.file_content(directory, fname, rev))
            except:
                import traceback
                traceback.print_exc()
                raise
        cnx.create_function('version_data', 1, version_data)

    sqlite_hooks = SQL_CONNECT_HOOKS.setdefault('sqlite', [])
    sqlite_hooks.append(init_sqlite_connection)


    # necesary posgres plpython initialization #################################

    def init_postgres_connection(cnx):
        # we'll have to initialize plpython sys.path since cw customize
        # it, as well as cubes.__path__, so give information using dedicated
        # sys_path_init registered procedure (in schema/_reproc.sql.postgres)
        import sys
        from os.path import join
        from cubicweb.cwconfig import CubicWebNoAppConfiguration
        # XXX enhance filtering
        stdlibdir = join(sys.prefix, 'lib')
        exportpath = [p for p in sys.path if not p.startswith(stdlibdir)]
        cubespath = CubicWebNoAppConfiguration.cubes_search_path()
        cu = cnx.cursor()
        # use '||'.join(exportpath) since plpython doesn't support sequence as
        # argument
        try:
            cu.execute('SELECT sys_path_init(%(syspath)s, %(cubespath)s)',
                       {'syspath': '||'.join(exportpath),
                        'cubespath': '||'.join(cubespath)})
            cnx.commit()
        except Exception, ex:
            print ('error while calling sys_path_init for posgtgres plpython '
                   'initialization: %s' % ex)
            print ("don't worry if you're creating the instance or migrating "
                   "vcsfile to 1.0")
            cnx.rollback()

    postgres_hooks = SQL_CONNECT_HOOKS.setdefault('postgres', [])
    postgres_hooks.append(init_postgres_connection)
