#!/usr/bin/python

import pygtk
import gtk
import gtk.glade
import gobject
import os
import sys
import threading
import time
import ocal
from pkg_resources import resource_string

import repository

__VERSION__ = '0.5a.0'
gladeFile = 'gui.glade'
try:
    gladeXML = resource_string(__name__, gladeFile)
except:
    gladeXML = file(os.path.join(os.path.dirname(__file__), 'gui.glade')).read()

SOURCE_LOCALDB = 1
SOURCE_OCAL = 2

class Indexer(object):

    def __init__(self, repo):

        self.repo = repo
        self.xml = gtk.glade.xml_new_from_buffer(gladeXML, len(gladeXML), 'indexer_window')
        self.xml.signal_autoconnect(self)
        self.window = self.xml.get_widget('indexer_window')

        self.treeview = self.xml.get_widget('indexer_treeview')
        self.liststore = gtk.ListStore(str)
        self.treeview.set_model(self.liststore)

        renderer = gtk.CellRendererText()
        self.pathcolumn = gtk.TreeViewColumn('Directory', renderer)
        self.pathcolumn.add_attribute(renderer, 'text', 0)
        self.treeview.append_column(self.pathcolumn)

        self.syncDirList()
        self.window.show()

    def syncDirList(self):
        "Make the list of indexed directories match the list stored in the repository"
        dirs = self.repo.getSetting('indexed_dirs')
        if dirs is None:
            dirs = ''
        dirs = dirs.splitlines()
        self.liststore.clear()
        for path in dirs:
            self.liststore.append([path])

    def __doIndexing(self, path, dialog):
        self.repo.indexDirectory(path)
        gobject.idle_add(dialog.destroy)
        gobject.idle_add(self.syncDirList)

    def indexDirectory(self, path):
        self.doneYet = False
        d = gtk.Dialog('Indexing clipart', flags=gtk.DIALOG_MODAL)
        l = gtk.Label('Please wait while we index your clipart')
        l.show()
        d.action_area.pack_start(l)
        d.show()
        t = threading.Thread(target=self.__doIndexing, args=[path, d], name='repository indexer')
        t.setDaemon(False)
        t.start()

    def on_indexer_window_destroy(self, widget):
        gtk.main_quit()

    def on_indexer_removebutton_clicked(self, widget):
        print 'remove button clicked'

    def on_indexer_addbutton_clicked(self, widget):
        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK)
        d = gtk.FileChooserDialog('Select clipart directory', parent=self.window, action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=buttons)
        d.set_default_response(gtk.RESPONSE_OK)
        response = d.run()
        path = d.get_filename()
        d.destroy()

        if response == gtk.RESPONSE_OK:
            try:
                self.indexDirectory(path)
            except:
                d = gtk.MessageDialog(flags=gtk.DIALOG_MODAL, buttons=gtk.BUTTONS_CLOSE, message_format="Error while indexing directory.", type=gtk.MESSAGE_ERROR)
                d.run()
                d.destroy()


    def on_indexer_okbutton_clicked(self, widget):
        self.window.destroy()

class Browser(object):

    iconSize = 60
    previewSize = 250
    numColumns = -1

    def __init__(self, repo):
        self.xml = gtk.glade.xml_new_from_buffer(gladeXML, len(gladeXML), 'mainwindow')
        self.xml.signal_autoconnect(self)

        self.repo = repo
        self.ocal = ocal.OCAL(repo)

        if self.repo.getSetting('indexed_dirs') is None:
            msg = "You don't appear to have any clipart indexed yet.  Would like to index some now?"
            d = gtk.MessageDialog(type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO, flags=gtk.DIALOG_MODAL, message_format=msg)
            response = d.run()
            d.destroy()
            if response == gtk.RESPONSE_YES:
                tempRepo = repository.Repository(repo.dbfile)
                indexer = Indexer(tempRepo)
                gtk.main()

        self.mainwindow = self.xml.get_widget('mainwindow')
        self.sidebar = self.xml.get_widget('sidebar')
        self.previewimage = self.xml.get_widget('previewimage')
        self.statusbar = self.xml.get_widget('statusbar')
        self.__statusContext = self.statusbar.get_context_id('browser')
        self.usertags_toggle = self.xml.get_widget('usertags_toggle')
        self.searchentry = self.xml.get_widget('searchentry')
        self.ocalentry = self.xml.get_widget('ocalentry')
        self.titleentry = self.xml.get_widget('titleentry')
        self.tagsentry = self.xml.get_widget('tagsentry')

        self.iconview = self.xml.get_widget('iconview')
        self.iconstore = gtk.ListStore(str, gtk.gdk.Pixbuf, gobject.TYPE_PYOBJECT)
        self.iconview.set_model(self.iconstore)
        self.iconview.set_text_column(0)
        self.iconview.set_pixbuf_column(1)
        self.iconview.set_columns(self.numColumns)

        # tag name, image count, user tag
        self.tagstore = gtk.ListStore(str, int, bool)
        self.tagstoreFiltered = self.tagstore.filter_new()
        self.tagstoreFiltered.set_visible_column(2)
        self.refreshTagsview()

        self.tagview = self.xml.get_widget('tagview')
        self.tagview.set_model(self.tagstore)

        renderer1 = gtk.CellRendererText()
        self.tagcolumn = gtk.TreeViewColumn('Tag', renderer1)
        self.tagcolumn.add_attribute(renderer1, 'text', 0)
        self.tagcolumn.set_resizable(True)
        self.tagview.append_column(self.tagcolumn)

        renderer2 = gtk.CellRendererText()
        self.imagecountcolumn = gtk.TreeViewColumn('Images', renderer2)
        self.imagecountcolumn.add_attribute(renderer2, 'text', 1)
        self.tagview.append_column(self.imagecountcolumn)

        self.mainwindow.maximize()
        self.mainwindow.show()

        gobject.idle_add(self.checkOCALAccess)

    def checkOCALAccess(self):
        if self.ocal.testAccess():
            self.ocalentry.set_sensitive(True)
        else:
            d = gtk.MessageDialog(flags=gtk.DIALOG_MODAL, buttons=gtk.BUTTONS_CLOSE, message_format="We were unable to access the Open Clipart Library.  This may mean that internet access is unavailable or that OCAL is experiencing technical difficulties.", type=gtk.MESSAGE_WARNING)
            d.run()
            d.destroy()
            self.ocalentry.set_sensitive(False)

    def on_ocalcheck_action(self, widget):
        gobject.idle_add(self.checkOCALAccess)

    def refreshTagsview(self):
        tags = self.repo.getTags()
        self.tagstore.clear()
        for name, data in sorted(tags.items()):
            self.tagstore.append([name, data[0], data[1]])

    def refreshQuery(self):
        source, query = self.__curQuery
        self.doQuery(source, query)

    # this method is threadsafe
    # meant to be called from a non-gtk thread, though it doesn't hurt if you use the gtk one
    def __doQuery(self, source, query):
        if source == SOURCE_LOCALDB:
            images = [self.repo.getImage(img) for img in self.repo.search(query)]
        elif source == SOURCE_OCAL:
            images = [self.repo.getImage(img) for img in self.ocal.search(query)]
        else: # implement online search here
            raise BrowserError()
        self.load_images(images)
        self.__curQuery = (source, query)

    def doQuery(self, source, query):
        t = threading.Thread(target=self.__doQuery, args=[source, query], name='search thread')
        t.start()

    def on_searchentry_activate(self, widget):
        self.doQuery(SOURCE_LOCALDB, self.searchentry.get_text())

    def on_ocalentry_activate(self, widget):
        query = self.ocalentry.get_text()
        print 'searching ocal: %s' % query
        self.doQuery(SOURCE_OCAL, query)

    def on_manage_action(self, widget):
        indexer = Indexer(self.repo)
        gtk.main()

    def on_usertags_toggle_toggled(self, widget):
        if self.usertags_toggle.get_active(): # if the button is toggled
            self.tagview.set_model(self.tagstoreFiltered)
        else:
            self.tagview.set_model(self.tagstore)

    def on_mainwindow_destroy(self, widget):
        self.on_quit_action(widget)

    def on_quit_action(self, widget):
        gtk.main_quit()

    def on_save_action(self, widget):
        img = self.getCurrentImg()
        if img is None:
            return
        xml = img.xml
        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK)
        d = gtk.FileChooserDialog('Save image', parent=self.mainwindow, action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=buttons)
        d.set_default_response(gtk.RESPONSE_OK)
        response = d.run()
        path = d.get_filename()
        d.destroy()

        if response != gtk.RESPONSE_OK:
            return

        try:
            file(path, 'w').write(xml)
        except:
            d = gtk.MessageDialog(flags=gtk.DIALOG_MODAL, buttons=gtk.BUTTONS_CLOSE, message_format="Error while saving image.", type=gtk.MESSAGE_ERROR)
            d.run()
            d.destroy()

    def getCurrentImg(self, imgOnly=True):
        items = self.iconview.get_selected_items()
        if len(items) == 0:
            return None

        itemPath = items[0]
        iter = self.iconstore.get_iter(itemPath)
        if imgOnly:
            return self.iconstore.get_value(iter, 2)
        else:
            return iter

    def on_iconview_selection_changed(self, widget):
        img = self.getCurrentImg()
        if img is None:
            self.previewimage.clear()
            self.titleentry.set_text('')
            self.tagsentry.set_text('')
        else:
            self.previewimage.set_from_pixbuf(img.largePixbuf)
            self.titleentry.set_text(img.title)
            self.tagsentry.set_text(', '.join(sorted(img.tags)))

    def load_images(self, images):
        gobject.idle_add(self.iconstore.clear)
        for img in images:
            gobject.idle_add(self.__addImage, img)
        gobject.idle_add(self.pushStatus, 'Found %i images' % len(images))

    def __addImage(self, img):
        self.iconstore.append((img.title, img.smallPixbuf, img))
        return False

    def on_tagview_cursor_changed(self, widget):
        model, iter = self.tagview.get_selection().get_selected()
        tag = model.get_value(iter, 0)
        self.doQuery(SOURCE_LOCALDB, 'tag:%s' % tag)

    def on_tagsentry_activate(self, widget):
        img = self.getCurrentImg()
        if img is None:
            self.tagsentry.set_text('')
            return
        text = self.tagsentry.get_text()
        tags = text.split(',')
        self.repo.updateTags(img.id, tags)
        self.refreshTagsview()
        self.refreshQuery()

    def on_titleentry_activate(self, widget):
        iter = self.getCurrentImg(False)
        img = self.iconstore.get_value(iter, 2)
        if iter is None:
            self.titleentry.set_text('')
            return
        newTitle = self.titleentry.get_text()
        self.repo.updateTitle(img.id, newTitle)
        self.iconstore.set(iter, 0, newTitle)
        img.title = newTitle


    def pushStatus(self, msg):
        self.statusbar.push(self.__statusContext, msg)
    
    def popStatus(self):
        self.statusbar.pop(self.__statusContext)

    def on_about_action(self, widget):
        d = gtk.AboutDialog()
        d.set_name('Clipart Browser')
        d.set_version(__VERSION__)
        d.set_website('http://www.openclipart.org')
        d.set_website_label('The Open Clipart Library')
        d.set_authors(['Greg Steffensen <greg.steffensen at gmail.com>'])
        d.run()
        d.destroy()


# TODO: research the conventions for storing user-specific program data on windows
def getStorageDir():
    "Finds the directory in which we should store program-related data, like the database and config file"
    return os.path.abspath(os.path.expanduser('~/.clipartbrowser'))


def run():
    gobject.threads_init()
    dbpath = os.path.join(getStorageDir(), 'images.db')

    try:
        repo = repository.Repository(dbpath)
    except repository.NoRepositoryError:
        print 'creating new repository at', dbpath
        repo = repository.Repository.createRepository(dbpath)
    except Exception, e:
        print e
        sys.exit('Unable to create new repository at %s' % dbpath)

    browser = Browser(repo)
    gtk.main()

if __name__ == '__main__':
    run()
