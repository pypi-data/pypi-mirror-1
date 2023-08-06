#!/usr/bin/python

import sys
import uuid
from gettext import ngettext

try:
    from lxml import etree
except ImportError:
    print "Please install lxml module"
    sys.exit(0)
    
DB_PATCH_SCHEMA = etree.XMLSchema(etree.XML("""
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="dbpatch">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="patch" maxOccurs="unbounded" >
                        <xs:complexType>
                            <xs:simpleContent>
                                <xs:extension base="xs:string">
                                    <xs:attribute name="id" type="xs:string" use="required" />
                                    <xs:attribute name="author" type="xs:string" use="required" />
                                    <xs:attribute name="comment" type="xs:string" use="optional" />
                                    <xs:attribute name="format" type="xs:string" use="optional" />
                                </xs:extension>
                            </xs:simpleContent>
                        </xs:complexType>
                </xs:element>
            </xs:sequence>
            <xs:attribute name="for_version" type="xs:string" use="required" />
            
        </xs:complexType>
    </xs:element>
</xs:schema>
"""))

class SqlDbPatch(object):
    format = 'SQL'
    def __init__(self, id, author, comment, body):
        self.id = id
        self.author = author
        self.comment = comment
        self.body = body
        

    def apply(self, cursor):
        cursor.execute(self.body)
        
    def __repr__(self):
        return u'SqlPatch("%s", "%s", "%s")' % (self.id, self.author, self.comment)

class PythonDbPatch(object):
    format = 'PYTHON'
    def __init__(self, id, author, comment, body):
        self.id = id
        self.author = author
        self.comment = comment
        self.body = body
        
        self.compiled_body = compile(body, "Change.%s" % id, 'exec')
        
    def apply(self, cursor):
        exec(self.body, {'cursor': cursor}, {})

    def __repr__(self):
        return u'PythonPatch("%s", "%s", "%s")' % (self.id, self.author, self.comment)

PATCH_FORMAT_MAP = {
    'sql': SqlDbPatch,
    'python': PythonDbPatch
}    

class DbPatchFile(object):
    def __init__(self, filename): 
        self.doc = etree.parse(filename)
#        DB_PATCH_SCHEMA = etree.XMLSchema(etree.parse(open('1.xml')))
        DB_PATCH_SCHEMA.assertValid(self.doc)
        
        self._parse()
        
    def _parse(self):
        root = self.doc.getroot()
        self.db_version = int(root.attrib['for_version'])
        
        patch_id_set = set()
        self.patches = []
        for p in root.iterchildren():
            if p.tag != 'patch':
                continue
            
            id = uuid.UUID(p.attrib['id'])
            
            if id in patch_id_set:
                raise Exception('Dublicated patch id detected (%s)' % id)
            else:
                patch_id_set.add(id)
            
            author = p.attrib['author']
            comment = p.attrib.get('comment', None)
            format = p.attrib.get('format', 'sql')
            body = p.text
            
            klass = PATCH_FORMAT_MAP[format]
            self.patches.append(klass(id, author, comment, body))

class DbPatcher(object):
    def __init__(self, database, host, port, user, password, verbose, patch_file=None):
        self.patch_file = patch_file
        self.verbose = verbose
        
        import psycopg2
        self.conn = psycopg2.connect("dbname='%s' host='%s' port=%d user='%s' password='%s'" % (database, host, port, user, password))
        self.cur = self.conn.cursor()
        
    def set_patch_file(self, patch_file):
        self.patch_file = patch_file
        
    def init(self):
        self.cur.execute("""
            SELECT count(*) from information_schema.tables WHERE table_name = 'db_version' and table_schema='public';
        """)
        data = self.cur.fetchone()
        if data[0]>0:
            if self.verbose>=1:
                print "Database has already initialized."
            return 0
        
        print "Initializing database...",
        self.cur.execute("""
            CREATE TABLE db_version
            (
              "version" integer NOT NULL,
              CONSTRAINT db_version_pkey PRIMARY KEY (version)
            );
            
            CREATE TABLE db_patches
            (
              id character varying(36) NOT NULL,
              CONSTRAINT db_patches_pkey PRIMARY KEY (id)
            );
            
            INSERT INTO db_version(version) values (1);                        
        """)
        self.conn.commit()
        print "Done"
        return 1
    def verify(self):
        self._assert_db_version()
        patches = self._filter_patches()
        
        if len(patches) == 0:
            if self.verbose>=1:
                print "Database is up to date"
            return 0
        
        if self.verbose>=1:
            print ngettext("%d patch needs to be applied", "%d patches needs to be applied", len(patches)) % len(patches)
            
        if self.verbose>=2:
            for p in patches:
                print "%s\t%s\t%s" % (p.id, p.author, p.comment)
        
        return len(patches) > 0
                
    def patch(self):
        self._assert_db_version()
        patches = self._filter_patches()
        if len(patches) == 0:
            if self.verbose>=1:
                print "Database is up to date"
            return 1
        if self.verbose>=1:
            print ngettext("Applying %d patch", "Applying %d patches", len(patches)) % len(patches)
        for p in patches:
            self._apply_patch(p)

        if self.verbose>=1:
            print "Successfuly applied."
        self.conn.commit()
        return 1

    def _assert_db_version(self):
        self.cur.execute('SELECT version FROM db_version')
        data = self.cur.fetchone()
        db_version = data[0]
        
        if db_version != self.patch_file.db_version:
            raise Exception('Database version does not match to a version defined in patch file.')
        
    def _filter_patches(self):
        return [p for p in self.patch_file.patches if not self._is_applied(p)]
    
    def _apply_patch(self, p):
        if self.verbose>=1:
            print "* %s (%s)..." % (p.comment, p.author),
        try:
            p.apply(self.cur)
            self.cur.execute('INSERT INTO db_patches (id) VALUES (%s)', [p.id.hex])
            
            if self.verbose>=1:
                print "Ok"
        except:
            if self.verbose>=1:
                print "Failed"
            raise

    def _is_applied(self, p):
        self.cur.execute('SELECT 1 FROM db_patches WHERE id=%s', [p.id.hex])
        return self.cur.rowcount > 0
        
        
def main():
    from optparse import OptionParser
    
    usage = "usage: %prog [options] init|verify|patch [patchfile.dbp]"

    parser = OptionParser(usage=usage)

    parser.add_option("-q", "--quiet", action="store_const", const=0, dest="verbose", help="don't print status messages to stdout")
    parser.add_option("-v", "--verbose", action="store_const", const=2, dest="verbose", help="print more status messages to stdout")
    parser.add_option("-s", "--host", action="store", type="string", dest="host", help="database host")
    parser.add_option("-p", "--port", action="store", type="int", dest="port", help="database port")
    parser.add_option("-u", "--user", action="store", type="string", dest="user", help="database user")
    parser.add_option("-w", "--pwd", action="store", type="string", dest="pwd", help="database password")
    parser.add_option("-d", "--db", action="store", type="string", dest="db", help="database name")
    
    parser.set_default('verbose', 1)
    parser.set_default('host', 'localhost')
    parser.set_default('port', 5432)

    (options, args) = parser.parse_args()

    if len(args)<1:
        parser.error("Please specify action.")
    elif len(args)>2:
        parser.error("Too many arguments.")
    
    p = DbPatcher(options.db, options.host, options.port, options.user, options.pwd, options.verbose)
    if args[0] != 'init' and len(args)==2:
        f = DbPatchFile(open(args[1]))
        p.set_patch_file(f)
    else:
        if args[0] != 'init':
            parser.error("Please specify patch file.")
        
    
    if args[0] == 'init':
        return p.init()
    elif args[0] == 'patch':
        return p.patch()
    elif args[0] == 'verify':
        return p.verify()
    else:
        parser.error("Unknown command")
        
if __name__=='__main__':
    main()