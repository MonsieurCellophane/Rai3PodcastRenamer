#!/usr/bin/env python
from __future__ import print_function
import pygtk
pygtk.require('2.0')
import gobject
import gtk

#from apache_log_parser_regex import dictify_logline c

class ApacheLogViewer(object):
    """Apache log file viewer which sorts on various pieces of data"""
    #the main window of the application
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL) 
        self.window.set_size_request(640, 480)
        self.window.maximize()
        #stop event loop on window destroy
        self.window.connect("destroy", self.quit)
        #a VBox is a container that holds other GUI objects primarily for layout
        self.outer_vbox = gtk.VBox()
        #toolbar which contains the open and quit buttons
        self.toolbar = gtk.Toolbar()
        #create open and quit buttons and icons
        #add buttons to toolbar
        #associate buttons with correct handlers
        open_icon = gtk.Image()
        quit_icon = gtk.Image()
        folder_icon  = gtk.Image()
        open_icon.set_from_stock(gtk.STOCK_OPEN, gtk.ICON_SIZE_LARGE_TOOLBAR)
        folder_icon.set_from_stock(gtk.STOCK_DIRECTORY, gtk.ICON_SIZE_LARGE_TOOLBAR)
        quit_icon.set_from_stock(gtk.STOCK_QUIT, gtk.ICON_SIZE_LARGE_TOOLBAR)
        self.open_button = gtk.ToolButton(icon_widget=open_icon)
        self.folder_button = gtk.ToolButton(icon_widget=folder_icon)
        self.quit_button = gtk.ToolButton(icon_widget=quit_icon)
        self.open_button.connect("clicked", self.show_file_chooser)
        self.folder_button.connect("clicked", self.show_folder_chooser)
        self.quit_button.connect("clicked", self.quit)
        self.toolbar.insert(self.open_button,  0)
        self.toolbar.insert(self.folder_button,1)
        self.toolbar.insert(self.quit_button,  2)
        #a control to select which file to open
        self.file_chooser = gtk.FileChooserWidget()
        self.file_chooser.connect("file_activated", self.load_logfile)
        #
        self.folder_chooser = gtk.FileChooserDialog(action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                                    parent=self.window,
                                                    buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        #a ListStore holds data that is tied to a list view
        #this ListStore will store tabular data of the form:
        #line_numer, remote_host, status, bytes_sent, logline
        self.loglines_store = gtk.ListStore(int, str, str, int, str)
        #associate the tree with the data...
        self.loglines_tree = gtk.TreeView(model=self.loglines_store)
        #...and set up the proper columns for it
        self.add_column(self.loglines_tree, 'Line Number', 0)
        self.add_column(self.loglines_tree, 'Remote Host', 1)
        self.add_column(self.loglines_tree, 'Status', 2)
        self.add_column(self.loglines_tree, 'Bytes Sent', 3)
        self.add_column(self.loglines_tree, 'Logline', 4)
        #make the area that holds the apache log scrollable
        self.loglines_window = gtk.ScrolledWindow()
        #pack things together
        self.window.add(self.outer_vbox)
        self.outer_vbox.pack_start(self.toolbar, False, False)
        self.outer_vbox.pack_start(self.file_chooser)
        self.outer_vbox.pack_start(self.loglines_window)
        self.loglines_window.add(self.loglines_tree)
        #make everythingvisible
        self.window.show_all()
        #but specifically hide the file chooser
        self.file_chooser.hide()
    
    def add_column(self, tree_view, title, columnId, sortable=True):
        column = gtk.TreeViewColumn(title, gtk.CellRendererText() , text=columnId)
        column.set_resizable(True)
        column.set_sort_column_id(columnId)
        tree_view.append_column(column)
        
    def show_file_chooser(self, widget, data=None):
        """make the file chooser dialog visible"""
        self.file_chooser.show()
        
    def show_folder_chooser(self, widget, data=None):
        """make the file chooser dialog visible"""
        #ALF self.folder_chooser.show()
        response=self.folder_chooser.run()
        if response == gtk.RESPONSE_ACCEPT: #_OK?
            print(self.folder_chooser.get_filename(), 'selected')
            import os
            os.chdir(self.folder_chooser.get_filename())
        elif response == gtk.RESPONSE_REJECT: #_CANCEL:?
            print('Closed, no files selected')
        else:
            print("WHAT? %r"%response)
        self.folder_chooser.hide() #destroy?
        
        
    def load_logfile(self, widget, data=None):
        """load logfile data into tree view"""
        filename = widget.get_filename()
        print("FILE-->", filename)
        self.file_chooser.hide()
        self.loglines_store.clear()
        logfile = open(filename, 'r')
        import random

        for i, line in enumerate(logfile):
            line_dict = {'remote_host':'foo.bar.com','status':'200 OK','bytes_sent':random.uniform(1000,100000)}
            self.loglines_store.append([i + 1, line_dict['remote_host'], line_dict['status'], int(line_dict['bytes_sent']), line])
        logfile.close()
        
    def quit(self, widget, data=None):
        """stop the main gtk event loop"""
        gtk.main_quit()
    def main(self):
        """start the gtk main event loop"""
        gtk.main()


l = ApacheLogViewer()
l.main()
