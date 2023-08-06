import os
from os.path import join, dirname
from cubicweb.server.sqlutils import sqlexec
from cubes.vcsfile.vcssource import get_vcs_source

# remove NOT NULL on VersionContent.data 
sync_schema_props_perms(('VersionContent', 'data', 'Bytes'), syncperms=False)

# dump the sqlite database
vcssource = get_vcs_source(repo)
dumpfile = '/tmp/vcsfile.%s.sql' % config.appid
dumpfile2 = '/tmp/vcsfile.%s.data.sql' % config.appid
if os.system("sqlite3 %s .dump > %s" % (vcssource.dbpath, dumpfile)):
    print 'error while dumping sqlite database'
    print 'is sqlite3 installed?'
    sys.exit(1)

# filter out schema statement, import only 'data' statements (eg INSERT) into
# the system database
session.set_pool()
cu = session.system_sql
status = None # None | 'data' | 'schema'
columns = []
stmt = None
for line in file(dumpfile):
    if status is None:
        try:
            stmttype, remaining = line.split(None, 1)
        except ValueError:
            print 'skip', repr(line)
            continue
        if stmttype == 'INSERT':
            status = 'data'
            assert columns
            # transform INSERT INTO "cw_Revision" into INSERT INTO cw_Revision
            # since the former is case sensitive while the later isn't
            insert, table, values = line.split('"', 2)
            # add columns name, they may be in different orders in the target
            # database
            line = '%s %s(%s) %s' % (insert, table, ','.join(columns), values)
        elif stmttype in ('CREATE', 'BEGIN', 'COMMIT'):
            columns = []
            status = 'schema'
        else:
            raise Exception('unknown statement type %s' % stmttype)
    if status == 'data':
        if stmt is None:
            stmt = line
        else:
            stmt += line
    else:
        print 'skip', repr(line)
    if status == 'schema':
        for w in line.split():
            w = w.replace('(', '').replace(')', '').strip()
            # islower to filter out table names
            if (w.startswith('cw_') or w.startswith('eid_')) and w.islower():
                columns.append(w)
            if w == 'CONSTRAINT':
                break
    if line.endswith(';\n'):
        status = None
        if stmt:
            cu(stmt)
        stmt = None

session.system_sql("UPDATE ENTITIES SET source='system' WHERE source='%s'"
                   % vcssource.uri)
session.commit()

# now inline from_repository
sync_schema_props_perms('from_repository', syncperms=False)

session.set_pool()
fpath = join(dirname(__file__), '..', 'schema', '_regproc.sql.postgres')
sqlexec(file(fpath).read(), session.system_sql, withpb=False, delimiter=';;')
session.commit()

# remove vcssource from sources file
sources = config.read_sources_file()
del sources[vcssource.uri]
config.write_sources_file(sources)


from cubes.vcsfile.bridge import set_at_revision

rset = rql('Revision X ORDERBY X', ask_confirm=False)
for reid, in rset:
    set_at_revision(session, reid, safetybelt=True)
checkpoint()
