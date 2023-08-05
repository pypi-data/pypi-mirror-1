#!/usr/bin/python
"""localocal.py- A module for local clip art repositories for the Clip Art Browser
Copyright (C) 2005 Greg Steffensen, greg.steffensen@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""
import shelve
import os
import shlex
from xml.dom import minidom
from xml.parsers import expat
import md5
import sys
import pkg_resources

# The permanent location of the configuration file... 
# this is the only location its permitted to be at
configPath = os.path.expanduser('~/.clipartbrowser/clipartbrowser.conf')

class API:
    "A clip art browser repository module api object"
    title = 'Local Clip Art'
    def __init__(self, config):
        self.config = config
        try:
            indexFile = config.get('localocal', 'indexfile')
            config.get('localocal', 'repodir')
            index = shelve.open(indexFile, flag='r', writeback=False)
        except Exception, e:
            print e
            index = self.indexGTK()
        assert index.has_key('keywords')
        self.kwIndex = index['keywords']
        self.pathIndex = index['paths']
        self.catIndex = index['categories']
        self.catsXML = index['catsXML']
        self.actions = [('Index local clip art', self.indexGTK)]

    def __updateConfig(self, repodir, indexFile):
        "Update the configuration file with a (possibly) new repository directory and index file path"
        c = self.config
        if not c.has_section('localocal'):
            c.add_section('localocal')
        c.set('localocal', 'repodir', os.path.abspath(repodir))
        c.set('localocal', 'indexFile', os.path.abspath(indexFile))
        if not os.path.exists(os.path.dirname(configPath)):
            os.mkdir(os.path.dirname(configPath))
        c.write(file(configPath, 'w'))

    def indexGTK(self, widget=None):
        indexer = GTKIndexer()
        if widget is None: # if this is being run at browser initialization time
            msg = "You have the local clip art repository enabled, but do not have a valid local clip art index.  You can create an index by selecting your top clip art directory below, or click cancel to skip loading this repository."
            repodir, indexFile, newIndex = indexer.index(chooseMessage=msg)
            self.__updateConfig(repodir, indexFile)
            return newIndex
        else:
            msg = None # otherwise, use the default message, and force the user to quit after
            try:
                repodir, indexFile, newIndex = indexer.index(chooseMessage=msg)
            except IndexingError:
                return
            self.__updateConfig(repodir, indexFile)
            dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_OK, message_format="Your clip art was indexed successfully.  The Clip Art Browser must now be restarted.  Click Ok to close the browser.")
            dialog.run()
            gtk.main_quit()
            sys.exit()

    def query(self, q):
        "Query using some custom query string format"
        queryTerms = [word.lower().replace(' ', '') for word in shlex.split(q)]
        if len(queryTerms) is 0:
            return []
        results = None
        
        for term in queryTerms:
            results = self.__processTerm(term, results)
        return [(img[0], img[1]) for img in results]

    def __processTerm(self, term, results):
        "Given a query term and a set of results retrieved so far, return the results with the new term factored in"
        if term.startswith('category:'):
            r = self.catIndex.get(term[len('category:'):], set()) 
        else:
            r = self.kwIndex.get(term, set())
        if results is None: # If this is the first query term in a list
            return r
        return results.intersection(r)

    def getImage(self, ID):
        # The second element should be a metadata dict, but we'll skip that for now
        img = self.pathIndex[ID]
        m = {'title':img[2], 'artist':img[3], 'keywords':img[4]}
        return (file(os.path.join(self.config.get('localocal', 'repodir'), ID)).read(), m)

# Code for the indexer
class Indexer(object):
    "A class that handles the indexing of local clip art"

    def index(self, rootdir, indexFile):
        "Actually do the indexing of the clip art"
        self.rootdir = os.path.normpath(rootdir) # remove the trailing slash, if any

        self.indexFile = os.path.normpath(indexFile)

        self.kwIndex = {}
        self.pathIndex = {}
        self.categoryIndex = {}

#       Setup the xml object that will be used to generate the xml category hierarchy
        self.xmlPaths = {}
        self.xmlDoc = minidom.Document()
        self.cat_hier = self.xmlDoc.createElement('category-hierarchy')
        self.xmlDoc.appendChild(self.cat_hier)
        self.xmlPaths[''] = self.cat_hier

        for dirpath, subdirs, filenames in os.walk(rootdir):
            if dirpath != rootdir:
                self._processDir(dirpath) # add the dir to the xml hierarchy
                for filename in filenames:
                    xml = file(os.path.join(dirpath, filename))
                    self._processFile(dirpath, filename)
        return self._saveIndex()

    def _processDir(self, dirpath):
#       The following code adds the directory to the xml category hierarchy
#       Since the root element gets a "category-hierarchy" element (already created),
#       not a "category" element, we skip this code for the root dir

        relativeDir = dirpath[len(self.rootdir) + 1:] # the relative path to the dir within the repository
        parentCategory, catname = os.path.split(relativeDir)
        el = self.xmlDoc.createElement('category')
        el.setAttribute('name', catname)
        el.setAttribute('id', relativeDir)
        self.xmlPaths[parentCategory].appendChild(el)
        self.xmlPaths[relativeDir] = el
        self.categoryIndex[relativeDir] = set()

    def _processFile(self, dirpath, filename):
        if not filename.endswith('.svg'): # we only index svg files (for now...)
            return
        fullpath = os.path.join(dirpath, filename)

        relpath = fullpath[len(self.rootdir) + 1:]
        try:
            xml = file(fullpath).read()
            m = getMetadata(xml)
        except: # If the metadata was not parsable, skip the image
            return
        contentsHash = md5.new(xml).hexdigest()
        c = (relpath, contentsHash, m.get('title', None), m.get('artist', None), tuple(m.get('keywords', [])))
        self.pathIndex[relpath] = c
        category = os.path.dirname(relpath)
        self.categoryIndex[category].add(c)
        for word in m.get('keywords', []):
            if self.kwIndex.has_key(word):
                self.kwIndex[word.lower()].update([c])
            else:
                self.kwIndex[word.lower()] = set([c])
                
    def _saveIndex(self):
        if not os.path.exists(os.path.dirname(self.indexFile)):
            os.mkdir(os.path.dirname(self.indexFile))
        persist = shelve.open(self.indexFile)
        persist['keywords'] = self.kwIndex
        persist['paths'] = self.pathIndex
        persist['categories'] = self.categoryIndex
        persist['catsXML'] = self.xmlDoc.toprettyxml()

        return persist

class GTKIndexer(Indexer):
    "A subclass of the basic Indexer that provides a GTK interface"

    chooseMessage = "Before your clip art can be indexed, you must choose the directory that your clip art is stored in."

    def __init__(self):
        global gtk
        import gtk
        import gtk.glade

    def index(self, indexFile=None, chooseMessage=None):
        "Index, showing gtk interfaces for choosing the repository dir and during the indexing process"
         
        if indexFile is None:
            indexFile = os.path.expanduser('~/.clipartbrowser/localindex.dat')
	glade_text = file(pkg_resources.resource_filename('ClipartBrowser.repositories', 'localocal.glade')).read()
        xml = gtk.glade.xml_new_from_buffer(glade_text, len(glade_text))
        chooseDialog = xml.get_widget('indexchoosedialog')
        chooseLabel = xml.get_widget('chooselabel')
        chooseLabel.set_text(chooseMessage or self.chooseMessage)
        repodirButton = xml.get_widget('dirchoosebutton')
        response = chooseDialog.run()
        repodir = repodirButton.get_filename()
        chooseDialog.destroy()
        if not response == gtk.RESPONSE_OK:
            raise IndexingError
        waitDialog = xml.get_widget('indexwaitdialog')
        waitDialog.connect('delete-event', lambda a, b: True)
        self.progresslabel = xml.get_widget('progresslabel')
        waitDialog.show()

#       Are these two lines necessary?
        while gtk.events_pending():
            gtk.main_iteration()

#       Do the actual indexing
        newIndex = super(GTKIndexer, self).index(repodir, indexFile)
        
        waitDialog.destroy()
        return repodir, indexFile, newIndex

    def _processDir(self, dirpath):
        "Update the gtk interface to indicate that we've started to index a new directory"
        self.progresslabel.set_markup('<b>Indexing %s</b>' % dirpath)
        while gtk.events_pending():
            gtk.main_iteration()

        super(GTKIndexer, self)._processDir(dirpath)

class _Metadata:

	svgNS = 'http://www.w3.org/2000/svg'
	dcNS = 'http://purl.org/dc/elements/1.1/'
	ccNS = 'http://web.resource.org/cc/'
	rdfNS = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'

	def __init__(self):
		self.path = []
		self.result = None
		self.keywords = [] # This will be implemented later
        
	def metadata_startElement(self, name, attrs):
		self.path.append(name)

	def metadata_endElement(self, name):
		self.path.pop()

	def metadata_charData(self, data):

		# Get title
 		if self.path[-1] == self.dcNS + ':title' and self.path[-2] == self.ccNS + ':Work':
			self.title = data

		# Get artist
		if self.path[-1] == self.dcNS + ':title' and self.path[-3] == self.dcNS + ':creator':
			self.artist  = data

		# Get keywords
		if self.path[-1] == self.rdfNS + ':li' and self.path[-3] == self.dcNS + ':subject':
			if getattr(self, 'keywords', None) is None:
				self.keywords = [data]
			else:
				self.keywords.append(data)
        
def getMetadata(svg):
	"Given the xml contents of an svg image, return a dict of its main metadata"
	metadata = {}
	parser = expat.ParserCreate(namespace_separator=':')
	m = _Metadata()
	parser.StartElementHandler = m.metadata_startElement
	parser.EndElementHandler = m.metadata_endElement
	parser.CharacterDataHandler = m.metadata_charData
	parser.Parse(svg)
	metadata['title'] = getattr(m, 'title', None)
	metadata['artist'] = getattr(m, 'artist', None)
	metadata['keywords'] = getattr(m, 'keywords', [])
	return metadata

class IndexingError(Exception):
    "There was some kind of problem while indexing local clip art"
    pass
