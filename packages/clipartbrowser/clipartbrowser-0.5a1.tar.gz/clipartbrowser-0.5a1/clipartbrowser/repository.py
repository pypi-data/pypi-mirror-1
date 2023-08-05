#!/usr/bin/python

# TODO
# add support for updating the repository... adding any new files in the given dirs, removing any entries
# that aren't there anymore (this should be done by md5sum, not by path, so that it magically is totally independent
# of how you organize the files on the FS)

try: # if you're using python 2.5
    import sqlite3
except: # if you're using python 2.4
    from pysqlite2 import dbapi2 as sqlite3

from lxml import etree
import md5
import os
import tempfile
from optparse import OptionParser
import sys
import threading
import string
from pyparsing import *
import gtk

namespaces = {
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'cc':  'http://web.resource.org/cc/',
    'dc':  'http://purl.org/dc/elements/1.1/',
    'svg': 'http://www.w3.org/2000/svg'
}

class Image(object):

    def __init__(self, meta, small, large):

        self.xml = meta['xml']
        self.id = meta['id']
        self.title = meta['title']
        self.author = meta['author']
        self.tags = set(meta['tags'])

        self.smallPixbuf = self.dictToPixbuf(small)
        self.largePixbuf = self.dictToPixbuf(large)

    @staticmethod
    def pixbufToDict(pixbuf):
        assert type(pixbuf) is gtk.gdk.Pixbuf
        d = {}
        d['width'] = pixbuf.get_width()
        d['height'] = pixbuf.get_height()
        d['has_alpha'] = pixbuf.get_has_alpha()
        d['bits_per_sample'] = pixbuf.get_bits_per_sample()
        d['rowstride'] = pixbuf.get_rowstride()
        d['data'] = pixbuf.get_pixels()
        return d

    @staticmethod
    def dictToPixbuf(data):
        w = data['width']
        h = data['height']
        a = data['has_alpha']
        b = data['bits_per_sample']
        r = data['rowstride']
        d = data['data']
        c = gtk.gdk.COLORSPACE_RGB
        pixbuf = gtk.gdk.pixbuf_new_from_data(d, c, h, b, w, h, r)
        return pixbuf

    @staticmethod
    def parseMetadata(xml):
        "Given the xml of an svg file, extract and return it's metadata (the relevent parts)"
        doc = etree.fromstring(xml)

        results = doc.xpath('svg:metadata/rdf:RDF/cc:Work/dc:title/text()', namespaces)
        if len(results) == 0:
            title = None
        else:
            title = results[0]

        results = doc.xpath('svg:metadata/rdf:RDF/cc:Work/dc:creator/cc:Agent/dc:title/text()', namespaces)
        if len(results) == 0:
            author = None
        else:
            author = results[0]

        tags = doc.xpath('svg:metadata/rdf:RDF/cc:Work/dc:subject/rdf:Bag/rdf:li/text()', namespaces)

        return {'title':title, 'author':author, 'tags':tags}


class Repository(object):
    "An api for accessing the local sqlite database"

    __local = threading.local()

    __term = Group(Optional(Word(alphas) + Suppress(':'), default='tag') + Word(alphas + nums + '_'))
    __conj = CaselessLiteral('and') ^ CaselessLiteral('or') ^ CaselessLiteral('not')
    __expr = StringStart() + __term + ZeroOrMore(__conj + __term) + StringEnd()

    SMALL_SIZE = 60
    LARGE_SIZE = 250

    @staticmethod
    def createRepository(filename, overwrite=False):
        "Create an empty new repository at a given filename"

        filename = os.path.abspath(filename)

        dirpath, filepath = os.path.split(filename)

        if os.path.exists(filename):
            if not overwrite:
                raise RepositoryExistsError()
            else:
                os.remove(filename)
        elif not os.path.isdir(dirpath):
            os.mkdir(dirpath)

        tableDefs = [
            '''CREATE TABLE images 
                (id INTEGER PRIMARY KEY, title, author, md5 UNIQUE NOT NULL, xml NOT NULL, 
                small_width INTEGER NOT NULL, small_height INTEGER NOT NULL, small_has_alpha INTEGER NOT NULL, 
                    small_rowstride INTEGER NOT NULL, small_bits_per_sample INTEGER NOT NULL, small_data BLOB NOT NULL,
                large_width INTEGER NOT NULL, large_height INTEGER NOT NULL, large_has_alpha INTEGER NOT NULL,
                    large_rowstride INTEGER NOT NULL, large_bits_per_sample INTEGER NOT NULL, large_data BLOB NOT NULL
                );''',
            'CREATE TABLE tags (name, image INTEGER, type);',
            'CREATE TABLE settings(key UNIQUE, value)',
            'CREATE INDEX tagsindex ON tags (name)'
        ]

        con = sqlite3.connect(filename)
        cur = con.cursor()
        for table in tableDefs:
            cur.execute(table)
        con.commit()
        con.close()

        return Repository(filename)

    def search(self, query):

        try:
            parsed = self.__expr.parseString(query).asList()
        except:
            raise InvalidQueryError()


        parsed.insert(0, 'or')
        results = set()
        while parsed:
            conj = parsed.pop(0)
            axis, value = parsed.pop(0)

            if axis == 'tag':
                newResults = self.tagQuery(value)
            else: # handle the other term types (title, author) here
                pass

            if conj == 'and':
                results = results.intersection(newResults)
            elif conj == 'or':
                results = results.union(newResults)
            elif conj == 'not':
                results = results.difference(newResults)

        return results

    def setSetting(self, key, value):
        self.cur.execute('DELETE FROM settings WHERE key=?', [key])
        self.cur.execute('INSERT INTO settings (key, value) VALUES (?, ?)', [key, value])
        self.commit()

    def getSetting(self, key):
        self.cur.execute('SELECT value FROM settings WHERE key=?', [key])
        results = self.cur.fetchall()
        if len(results) == 0:
            return None
        else:
            return results[0][0]


    def __init__(self, dbfile):
        self.dbfile = dbfile
        if not os.access(dbfile, os.R_OK):
            raise NoRepositoryError()

        self.__imgCache = {}

    def __getCur(self):
        try:
            return self.__local.cur
        except:
            self.__local.con = sqlite3.connect(self.dbfile)
            self.__local.con.row_factory = sqlite3.Row
            self.__local.cur = self.__local.con.cursor()
            return self.__local.cur


    cur = property(__getCur)

    def commit(self):
        self.__local.con.commit()


    def tagQuery(self, tag):
        "Find all images with a given tag, return their id's as a set"
        tag = tag.lower().strip()
        results = self.cur.execute('SELECT image FROM tags WHERE name = ?', [tag])
        return set([result[0] for result in results])

    def getTags(self):
        "Return a dict of all the tags in the db, with dict values being a (images, is a user tag) duple"
        names = [row[0] for row in self.cur.execute('SELECT DISTINCT name FROM tags').fetchall()]
        tags = {}
        for name in names:
            images = self.cur.execute('SELECT count(image) FROM tags WHERE name=?', [name]).fetchone()[0]
            isNew = self.cur.execute('SELECT count(name) FROM tags WHERE name=? AND type="user"', [name]).fetchone()[0] > 0
            tags[name] = (images, isNew)
        return tags

    def getImage(self, id):
        "Given an image id, retrieve its contents and return as an image object"

        if self.__imgCache.has_key(id):
            return self.__imgCache[id]
       
        self.cur.execute('SELECT * FROM images WHERE id=?', [id]) # naughty naughty :)
        if self.cur.rowcount == 0:
            raise InvalidID(id)

        imgData = self.cur.fetchone()

        metaCols = ['id', 'xml', 'title', 'author']
        smallCols = ['small_width', 'small_height', 'small_rowstride', 'small_has_alpha', 'small_bits_per_sample', 'small_data']
        largeCols = ['large_width', 'large_height', 'large_rowstride', 'large_has_alpha', 'large_bits_per_sample', 'large_data']

        meta = {}
        for col in metaCols:
            meta[col] = imgData[col]

        small = {}
        for col in smallCols:
            small[col[6:]] = imgData[col]

        large = {}
        for col in largeCols:
            large[col[6:]] = imgData[col]

        self.cur.execute('SELECT name FROM tags WHERE image=?', [id])
        meta['tags'] = [row[0] for row in self.cur.fetchall()]

        newImg = Image(meta, small, large)
        self.__imgCache[id] = newImg 
        return newImg

    def addImage(self, filename=None, xml=None):
        "Given an image object, insert it into the repository"
        print 'addImage: %s' % filename

        assert filename is not None or xml is not None

        if filename is None:
            tempname = tempfile.mkstemp(suffix='.svg')[1]
            temp = file(tempname, 'w')
            temp.write(xml)
            temp.close()
            smallPixbuf = gtk.gdk.pixbuf_new_from_file_at_size(tempname, self.SMALL_SIZE, self.SMALL_SIZE)
            largePixbuf = gtk.gdk.pixbuf_new_from_file_at_size(tempname, self.LARGE_SIZE, self.LARGE_SIZE)
            os.remove(tempname)
        else:
            f = file(filename)
            xml = f.read()
            f.close()
            smallPixbuf = gtk.gdk.pixbuf_new_from_file_at_size(filename, self.SMALL_SIZE, self.SMALL_SIZE)
            largePixbuf = gtk.gdk.pixbuf_new_from_file_at_size(filename, self.LARGE_SIZE, self.LARGE_SIZE)


        m = md5.new()
        m.update(xml)
        img_md5 = m.hexdigest()

        small = Image.pixbufToDict(smallPixbuf)
        large = Image.pixbufToDict(largePixbuf)
        meta = Image.parseMetadata(xml)

        q = '''INSERT INTO images (title, author, md5, xml,
                    small_width, small_height, small_has_alpha, small_rowstride, small_bits_per_sample, small_data,
                    large_width, large_height, large_has_alpha, large_rowstride, large_bits_per_sample, large_data) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        try:
            self.cur.execute(q, 
                [meta['title'], meta['author'], img_md5, xml,
                small['width'], small['height'], small['has_alpha'], small['rowstride'], small['bits_per_sample'], buffer(small['data']),
                large['width'], large['height'], large['has_alpha'], large['rowstride'], large['bits_per_sample'], buffer(large['data'])
            ])
            newid = self.cur.execute('SELECT last_insert_rowid()').fetchone()[0]
        except sqlite3.IntegrityError:
            raise DuplicateImageError()

        for tag in meta['tags']:
            tag = self.normalizeTag(tag)
            if self.tagFilter(tag):
                self.cur.execute('INSERT INTO tags (name, image, type) VALUES (?, ?, "original")', [tag, newid])

        self.commit()
        return newid

    @staticmethod
    def normalizeTag(tag):
        return tag.strip().lower().replace(' ', '_')

    @staticmethod
    def tagFilter(tag):
        "Filter function to remove certain useless tags that happen to populate ocal"
        if tag.startswith('hash('):
            return False
        if tag[0] not in string.ascii_lowercase:
            return False
        return True

    def updateTags(self, id, tags, updateType='user', doDeletes=True):
        tags = set([self.normalizeTag(tag) for tag in tags])
        self.cur.execute('SELECT name FROM tags where image=?', [id])
        oldTags = set([row[0] for row in self.cur.fetchall()])
        for tag in tags.difference(oldTags):
            self.cur.execute('INSERT INTO tags (name, image, type) VALUES (?, ?, ?)', [tag, id, updateType])
        if doDeletes:
            for tag in oldTags.difference(tags):
                self.cur.execute('DELETE FROM tags WHERE name=? AND image=?', [tag, id])
        if self.__imgCache.has_key(id):
            self.__imgCache[id].tags = tags
            del self.__imgCache[id]
        self.commit()

    def updateTitle(self, id, title, updateType='user'):
        self.cur.execute('UPDATE images SET title=? WHERE id=?', [title, id])
        self.commit()

    def removeImage(self, id):
        self.cur.execute('DELETE FROM images WHERE id=?', [id])
        self.cur.execute('DELETE FROM tags WHERE image=?', [id])
        self.commit()

    def indexDirectory(self, path):
        "Bulk insert of every image in a directory"

        path = os.path.abspath(path)

        errors = []
        for root, dirs, files in os.walk(path):
            for filename in files:
                if filename.endswith('.svg'):
                    fullpath = os.path.join(root, filename)
                    try:
                        self.addImage(filename=fullpath)
                    except Exception, e:
                        errors.append(fullpath)
        dirs = self.getSetting('indexed_dirs')
        if dirs:
            dirs = dirs.splitlines()
        else:
            dirs = []
        dirs.append(path)
        self.setSetting('indexed_dirs', '\n'.join(dirs))
        return errors


class BrowserError(Exception):
    "A clipart browser specific error"
    pass

class InvalidQueryError(BrowserError):
    "The user entered a query string with invalid syntax"
    pass
class NoRepositoryError(BrowserError):
    "Attempted to open a repository in a file that doesn't exist"
    pass
class RepositoryExistsError(BrowserError):
    "Attempted to create a new repository at a path that already exists"
    pass
class DuplicateImageError(BrowserError):
    "An attempt to insert an image that's already in the database (as determined by comparing md5 sums)"
    pass
class InvalidIDError(BrowserError):
    "Attempt to access an image by an id that doesn't exist"
    pass

if __name__ == '__main__':
    parser = OptionParser(usage='usage: %prog [options] FILE')
    parser.add_option('-c', '--create', action='store_true', help='create an empty new clipart index database at FILE')
    parser.add_option('-f', '--force', action='store_true', help='overwrite any existing repository at FILE when creating new one')
    parser.add_option('-i', '--index', metavar='DIR', help='add the clipart in directory DIR to the index at FILE')

    options, args = parser.parse_args()
    if options.create:
        overwrite = getattr(options, 'force', False)
        print 'creating new repository at', args[0]
        try:
            repo = Repository.createRepository(args[0], overwrite)
        except RepositoryExistsError:
            sys.exit('ERROR: there is already a file at path "%s".  Try using the "-f" flag' % args[0])
    else:
        repo = Repository(args[0])
    if options.index:
        print 'indexing clipart at %s' % options.index
        repo.indexDirectory(options.index)

