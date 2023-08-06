# -*- coding: iso-8859-1 -*-
#!/usr/bin/env python
# hgview.py - gtk-based hgk
#
# Copyright (C) 2007 Logilab. All rights reserved.
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.
"""
Main gtk application for hgview
"""
import sys, os
import time
import re
from optparse import OptionParser
from os.path import dirname, join, isfile

import gtk
import gtk.glade
import gobject
import pango

import hgview.fixes

from graphrenderer import RevGraphRenderer
from diffstatrenderer import DiffStatRenderer
from hgview.hgrepo import HgHLRepo, short_hex, short_bin


GLADE_FILE_NAME = "hgview.glade"


def watch_displayed(meth):
    """
    Method to be used as a decorator. The decorated method will
    have automatically a watch displayed until they return.
    Works less reliably than watch_displayed, but can returns something...
    """
    assert callable(meth)

    def watched(self, *args, **kw):
        watch = gtk.gdk.Cursor(gtk.gdk.WATCH)
        w = self.xml.get_widget('window_main')
        w.window.set_cursor(watch)
        # Give the mainloop a chance to change the cursor
        # This might be dangerous!
        gtk.main_iteration(block=False)
        try:
            ret = meth(self, *args, **kw)
            return ret
        finally:
            w.window.set_cursor(None)
    return watched


def load_glade(root=""):
    """Try several paths in which the glade file might be found"""
    for _path in [dirname(__file__),
                  join(sys.exec_prefix, 'share/hgview'),
                  os.path.expanduser('~/share/hgview'),
                  join(dirname(__file__), "../../../../share/hgview"),
                  join(dirname(__file__), "../../../../../share/hgview"),
                  ]:
        glade_file = join(_path, GLADE_FILE_NAME)
        if isfile(glade_file):
            break
    else:
        raise ValueError("Unable to find hgview.glade."
                         "Check your installation.")
    return gtk.glade.XML(glade_file, root)

#import hotshot
#PROF = hotshot.Profile("/tmp/hgview.prof")

DIFFHDR = "=== %s ===\n"
M_ID = 0
M_NODE = 1
M_NODEX = 2
M_EDGES = 3
M_DATE = 4
M_GRAPHORDER = 5
M_AUTH = 6
M_AUTHCOLOR = 7
M_REV = 8



def make_texttag( name, **kwargs ):
    """Helper function generating a TextTag"""
    tag = gtk.TextTag(name)
    for key, value in kwargs.items():
        key = key.replace("_","-")
        try:
            tag.set_property( key, value )
        except TypeError:
            print "Warning the property %s is unsupported in this version of pygtk" % key
    return tag

class HgViewApp(object):
    """Main hg view application"""
    def __init__(self, repo, filerex = None ):
        self.xml = load_glade("window_main")
        self.xml.signal_autoconnect( self )
        statusbar = self.xml.get_widget("statusbar1")
        self.progressbar = gtk.ProgressBar()
        self.progressbar.hide()
        statusbar.pack_start( self.progressbar )
        self.repo = repo
        self.filerex = filerex
        if filerex:
            self.filter_files = re.compile( filerex )
        else:
            self.filter_files = None
        self.filter_noderange = None
        self.branch_selected = None
        self.SHOW_GRAPH = True
        # The strings are stored as PYOBJECT when they contain zeros and also
        # to save memory when they are used by the custom renderer
        self.revisions = gtk.ListStore( gobject.TYPE_PYOBJECT, # node id
                                        gobject.TYPE_PYOBJECT, # node
                                        gobject.TYPE_PYOBJECT, # x for the node
                                        gobject.TYPE_PYOBJECT, # lines to draw
                                        gobject.TYPE_FLOAT, # date
                                        gobject.TYPE_INT64, # natural order
                                        gobject.TYPE_STRING, # author
                                        gobject.TYPE_STRING, # author color
                                        gobject.TYPE_INT64, # node id
                                        )

        self.filelist = gtk.ListStore( gobject.TYPE_STRING, # filename
                                       gobject.TYPE_STRING,  # markname
                                       gobject.TYPE_PYOBJECT, # diffstat
                                       )
        self.graph = None
        self.find_text = None
        self._idletask_id = None

        self.setup_tags()
        self.setup_tree()
        self.init_filter()
        self.refresh_tree()
        self.create_revision_popup()
        self.setup_combo('branch_highlight_combo')

    def create_revision_popup(self):
        self.revpopup_path = None, None
        tree = self.xml.get_widget( "treeview_revisions" )
        self.revpopup = gtk.Menu()
        self.revpopup.attach_to_widget( tree, None)

        m1 = gtk.MenuItem("Add tag...")
        m1.show()
        m1.connect("activate", self.revpopup_add_tag)
        self.revpopup.attach(m1, 0, 1, 0, 1)
        # not yet implemented, disactivate
        m1.set_sensitive(False)

        m2 = gtk.MenuItem("Update")
        m2.show()
        m2.connect("activate", self.revpopup_update)
        self.revpopup.attach(m2, 0, 1, 1, 2)
        # not yet implemented, disactivate
        m2.set_sensitive(False)

    def revpopup_add_tag(self, item):
        raise NotImplementedError()
        
    def revpopup_update(self, item):
        raise NotImplementedError()

    def setup_combo(self, combo_name):
        combo_filter = self.xml.get_widget(combo_name)
        self.branch_store = gtk.ListStore( gobject.TYPE_STRING )
        combo_filter.set_model(self.branch_store)
        if combo_name == 'branch_highlight_combo':
            self.branch_store.append( ('All',) )
        for branch_name in self.repo.get_branch().keys():
            self.branch_store.append( (branch_name,) )
        combo_filter.set_active(0)
 
    def get_node_branches(self):
        branch_nodeRev = {}
        dic_branch, _unknown, _tip_rev = self.repo.get_branches_heads()
        for branch, node in dic_branch.items():
            node_info = self.repo.read_node(node)
            rev = node_info.rev
            branch_nodeRev[rev] = branch
        return branch_nodeRev
        
    def on_refresh_activate(self, arg):
        self.repo.refresh()
        self.refresh_tree()
        
    def filter_nodes(self):
        """Filter the nodes according to filter_files and filter_nodes"""
        if not self.filter_files and not self.filter_noderange:
            return self.repo.nodes
        
        keepnodes = []
        nodes = self.repo.nodes
        frex = self.filter_files
        noderange = self.filter_noderange or set(range(len(nodes)))
        hide_otherbranches = self.xml.get_widget("branch_checkbox").get_active()
        branch_selected = self.branch_selected
        for n in nodes:
            node = self.repo.read_node(n)
            if node.rev in noderange:
                if hide_otherbranches:
                    if node.branches['branch'] != branch_selected and branch_selected != 'All':
                        continue
                if not node.files: 
                    keepnodes.append(n)
                else:
                    for f in node.files:
                        if frex.search(f):
                            keepnodes.append( n )
                            break
  
        tree = self.xml.get_widget( "treeview_revisions" )
        file_filter = self.xml.get_widget("entry_file_filter").get_text()
        if file_filter:
            col = tree.get_column(0)
            self.revisions.set_sort_column_id(M_REV, gtk.SORT_ASCENDING)
            self.SHOW_GRAPH = False
        else:
            col = tree.get_column(1)
            self.revisions.set_sort_column_id(M_GRAPHORDER, gtk.SORT_ASCENDING)
            self.SHOW_GRAPH = True
        
        return keepnodes

    def on_window_main_delete_event( self, win, evt ):
        """Bye"""
        gtk.main_quit()

    def on_quit1_activate( self, *args ):
        """Bye"""
        gtk.main_quit()

    def on_about_activate(self, *args):
        """ Display about dialog """
        dlg=gtk.AboutDialog()
        dlg.set_authors([u'Ludovic Aubry',
                         u'Aur�lien Camp�as',
                         u'David Douard',
                         u'Graziella Toutoungis',
                         ])
        from hgview.__pkginfo__ import modname, version, short_desc, long_desc
        dlg.set_comments(short_desc)
        dlg.set_name(modname)
        dlg.set_version(version)
        #dlg.set_logo(pixbuf)
        dlg.run()
        dlg.destroy()

    def setup_tags(self):
        """Creates the tags to be used inside the TextView"""
        textwidget = self.xml.get_widget( "textview_status" )
        text_buffer = textwidget.get_buffer()
        tag_table = text_buffer.get_tag_table()
       
        tag_table.add( make_texttag( "mono", family="Monospace" ))
        tag_table.add( make_texttag( "blue", foreground='blue' ))
        tag_table.add( make_texttag( "red", foreground='red' ))
        tag_table.add( make_texttag( "green", foreground='darkgreen' ))
        tag_table.add( make_texttag( "black", foreground='black' ))
        tag_table.add( make_texttag( "greybg",
                                     paragraph_background='grey',
                                     weight=pango.WEIGHT_BOLD ))
        tag_table.add( make_texttag( "yellowbg", background='yellow' ))
        link_tag = make_texttag( "link", foreground="blue",
                                 underline=pango.UNDERLINE_SINGLE )
        link_tag.connect("event", self.link_event )
        tag_table.add( link_tag )
        textwidget.connect("motion-notify-event", self.text_widget_move )

    def text_widget_move(self, widget, event):
        cursor = gtk.gdk.Cursor(gtk.gdk.XTERM)
        widget.get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(cursor)

    def link_event( self, tag, widget, event, iter_ ):
        """Handle a click on a 'link' tag in the main TextView"""
        if event.type == gtk.gdk.MOTION_NOTIFY and not (
            event.state & (gtk.gdk.BUTTON1_MASK|gtk.gdk.BUTTON2_MASK|gtk.gdk.BUTTON3_MASK)
            ):
            # we change cursor only if no button is pressed
            cursor = gtk.gdk.Cursor(gtk.gdk.HAND2)
            widget.get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(cursor)
            # return true so the event is not passed through to text_widget_move
            return True
        if event.type != gtk.gdk.BUTTON_RELEASE:
            return
        text_buffer = widget.get_buffer()
        beg = iter_.copy()
        while not beg.begins_tag(tag):
            beg.backward_char()
        end = iter_.copy()
        while not end.ends_tag(tag):
            end.forward_char()
        text = text_buffer.get_text( beg, end )

        it = self.revisions.get_iter_first()
        while it:
            node = self.revisions.get_value( it, M_ID )
            hhex = short_hex(node)
            if hhex == text:
                break
            it = self.revisions.iter_next( it )
        if not it:
            return
        tree = self.xml.get_widget("treeview_revisions")
        sel = tree.get_selection()
        sel.select_iter(it)
        path = self.revisions.get_path(it)
        tree.scroll_to_cell( path )


    def author_data_func( self, column, cell, model, iter_, user_data=None ):
        """A Cell datafunction used to provide the author's name and
        foreground color"""
        node = model.get_value( iter_, M_NODE )
        branch = node.branches['branch']
        cell.set_property( "text", self.repo.authors[node.author_id] )
        cell.set_property( "foreground", self.repo.colors[node.author_id] )


    def rev_data_func( self, column, cell, model, iter_, user_data=None ):
        """A Cell datafunction used to provide the revnode's text"""
        node = model.get_value( iter_, M_NODE )
        cell.set_property( "text", str(node.rev) )
        row = model[iter_]

    def date_data_func( self, column, cell, model, iter_, user_data=None ):
        """A Cell datafunction used to provide the date"""
        node = model.get_value( iter_, M_NODE )
        cell.set_property( "text", node.date )
        reversed = column.get_sort_order() == gtk.SORT_DESCENDING

        row = model[iter_]
   
         
    def files_data_func( self, column, cell, model, iter_, user_data=None ):
        """A Cell datafunction used to provide the files"""
        node = model.get_value( iter_, 0 )
        
        txt = self.xml.get_widget( "entry_find" ).get_text()
        str_node = str(node).replace('&', '&amp;').replace('<', '&lt;')
        if txt !='':
            try:
                rexp = re.compile( '(%s)' % txt.replace('&', '&amp;').replace('<', '&lt;') )
                markup = rexp.sub('<span background="yellow">\\1</span>', str_node)
            except:
                # regexp incorrect
                markup = str_node
        else:
            markup = str_node
        cell.set_property("markup", '<span>%s</span>' % markup)
  
    def setup_tree(self ):
        """Configure the 2 gtk.TreeView"""
        # Setup the revisions treeview
        tree = self.xml.get_widget( "treeview_revisions" )
        tree.get_selection().connect("changed", self.selection_changed )

        rend = gtk.CellRendererText()
        col = gtk.TreeViewColumn("ID", rend, text=M_REV)
        col.set_sort_column_id(M_REV)
        col.set_resizable(True)
        col.connect("clicked", self.sort_on_id)
        tree.append_column( col )

        rend = RevGraphRenderer(self)
        rend.connect( "activated", self.cell_activated )
        self.graph_rend = rend
        col = gtk.TreeViewColumn("Log", rend, nodex=M_NODEX, edges=M_EDGES,
                                 node=M_NODE)
        col.set_resizable(True)
        col.set_sizing( gtk.TREE_VIEW_COLUMN_FIXED )
        col.set_fixed_width(400)
        col.set_sort_column_id(M_GRAPHORDER)
        col.connect("clicked", self.sort_on_id)
        tree.append_column(col)

        rend = gtk.CellRendererText()
        col = gtk.TreeViewColumn("Author", rend, text=M_AUTH, foreground=M_AUTHCOLOR)
        #col.set_cell_data_func( rend, self.author_data_func )
        col.set_resizable(True)
        col.set_sort_column_id(M_AUTH)
        col.connect("clicked", self.sort_on_id)
        tree.append_column(col)

        rend = gtk.CellRendererText()
        col = gtk.TreeViewColumn("Date", rend )
        col.set_cell_data_func( rend, self.date_data_func )
        col.set_resizable(True)
        col.set_sort_column_id(M_DATE)
        col.connect("clicked", self.sort_on_id)
        tree.append_column( col )

        tree.set_model(self.revisions )
            
        ##Setup the filelist treeview
        tree_files = self.xml.get_widget( "treeview_filelist" )
        #tree_files.set_rules_hint( 1 )
        tree_files.get_selection().connect("changed", self.fileselection_changed )

        rend = gtk.CellRendererText()
        col = gtk.TreeViewColumn("Files", rend,  text=0)
        col.set_cell_data_func( rend, self.files_data_func )
        col.set_reorderable(True)
        col.set_resizable(True)
        tree_files.append_column( col )
        tree_files.set_model( self.filelist )
       
        rend = DiffStatRenderer()
        col = gtk.TreeViewColumn("Diff Stat", rend, stats=2 )
        col.set_reorderable(True)
        tree_files.append_column( col )

        tree_files.set_model( self.filelist )
        
    def sort_on_id(self, *args):
        sorted_column = args[0].get_sort_column_id()
        sort_type = args[0].get_sort_order().value_nick
        if sort_type == 'ascending':
            if sorted_column == 5:
                self.SHOW_GRAPH = True
            else:
                self.SHOW_GRAPH = False 
        else:
            self.SHOW_GRAPH = False
        return self.SHOW_GRAPH 
              
    def cell_activated(self, *args):
        print "nudge"

    def refresh_tree(self):
        """Starts the process of filling the ListStore model"""
        if self._idletask_id is not None:
            self._idletask_id = None
            gobject.main_context_default().iteration(True)
        self.repo.read_nodes()
        todo_nodes = self.filter_nodes()
        graph = self.repo.graph( todo_nodes )
        self.graph_rend.set_colors( graph.colors )

        self.revisions.clear()
        self.progressbar.show()
        self.last_node = 0
        self.graph = graph
        self._idletask_id = gobject.idle_add( self.idle_fill_model )
        return

  
    def on_treeview_revisions_button_press_event(self, treeview, event):
        if event.button==3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = treeview.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                treeview.grab_focus()
                treeview.set_cursor( path, col, 0)
                self.revpopup_path = path, col
                self.revpopup.popup( None, None, None, event.button, time)
            return 1

    def idle_fill_model(self):
        """Idle task filling the ListStore model chunks by chunks"""
        if self._idletask_id is None:
            # self._idletask_id has been set to None, which means we
            # want to cancel the background task of filling the tree
            # model
            self.graph = None
            self.rowselected = None
            self.progressbar.hide()
            return False
        NMAX = 300  # Max number of entries we process each time
        graph = self.graph
        N = self.last_node
        graph.build(NMAX)
        rowselected = self.graph.rows
        add_rev = self.revisions.append
        tree = self.xml.get_widget( "treeview_revisions" )
        tree.freeze_notify()

        # compute the final bound of this run
        last_node = min(len(rowselected), N + NMAX)
        for n in xrange(N, last_node ):
            node = rowselected[n]
            if node is None:
                continue
            rnode = self.repo.read_node( node )
            lines = graph.rowlines[n]
            auth = self.repo.authors[rnode.author_id] 
            authcolor = self.repo.colors[rnode.author_id] 
            rev = int(rnode.rev)
            add_rev( (node, rnode, graph.x[node], (lines,n), time.mktime(rnode.localtime), n, auth, authcolor, rev) )

        self.last_node = last_node
        tree.thaw_notify()
        self.progressbar.set_fraction( float(self.last_node) / len(rowselected) )
        if self.last_node == len(rowselected):
            self.graph = None
            self.rowselected = None
            self.progressbar.hide()
            self._idletask_id = None
            return False
        return True

    def set_revlog_header( self, buf, node, rnode ):
        """Put the revision log header in the TextBuffer"""
        repo = self.repo
        eob = buf.get_end_iter()
        buf.insert( eob, "Revision: %d:" % rnode.rev )
        buf.insert_with_tags_by_name( eob, short_hex(node), "link" )
        buf.insert( eob, "\n" )
        buf.insert( eob, "Branch: %s\n" % self.repo.read_node(node).branches['branch'])
        buf.insert( eob, "Author: %s\n" %  repo.authors[rnode.author_id] )
        buf.create_mark( "begdesc", buf.get_start_iter() )
        
        for p in repo.parents(node):
            pnode = repo.read_node(p)
            short = short_hex(p)
            buf.insert( eob, "Parent: %d:" % pnode.rev )
            buf.insert_with_tags_by_name( eob, short, "link" )
            buf.insert(eob, "(%s)\n" % pnode.short)
        for p in repo.children(node):
            pnode = repo.read_node(p)
            short = short_hex(p)
            buf.insert( eob, "Child:  %d:" % pnode.rev )
            buf.insert_with_tags_by_name( eob, short, "link" )
            buf.insert(eob, "(%s)\n" % pnode.short)

        buf.insert( eob, "\n" )


    def prepare_diff(self, difflines, offset, diffmsg, changes):
        idx = 0
        outlines = []
        tags = []
        filespos = []
        def addtag( name, offset, length ):
            if tags and tags[-1][0] == name and tags[-1][2]==offset:
                tags[-1][2] += length
            else:
                tags.append( [name, offset, offset+length] )
        stats = [0,0]
        statmax = 0
        if diffmsg:
            DIFFHDR = ""
            for i, key in enumerate(diffmsg.split("\n")):
                if i < len(diffmsg.split("\n"))-1:
                    msg = key.split(':')[0]
                    DIFFHDR += "===%s===\n" % msg
            txt = DIFFHDR
            addtag("greybg", offset, len(txt))
            outlines.append(txt)
            markname = "file%d" % idx
            statmax = max( statmax, stats[0]+stats[1] )
            stats = [0,0]
            for file_added in changes[1]:
                idx += 1
                markname = "file%d" % idx
                statmax = max( statmax, stats[0]+stats[1] )
                stats = [0,0] 
                filespos.append(( file_added , markname, offset, stats ))
                offset += len(txt) 
        else:

            for i,l in enumerate(difflines):
                if l.startswith("diff"):
                    f = l.split()[-1]
                    DIFFHDR = "=== %s ===\n"
                    txt = DIFFHDR % f
                    addtag( "greybg", offset, len(txt) )
                    outlines.append(txt)
                    markname = "file%d" % idx
                    idx += 1
                    statmax = max( statmax, stats[0]+stats[1] )
                    stats = [0,0]
                    filespos.append(( f, markname, offset, stats ))
                    offset += len(txt)
                    continue
                elif l.startswith("+++"):
                    continue
                elif l.startswith("---"):
                    continue
                elif l.startswith("+"):
                    tag = "green"
                    stats[0] += 1
                elif l.startswith("-"):
                    stats[1] += 1
                    tag = "red"
                elif l.startswith("@@"):
                    tag = "blue"
                else:
                    tag = "black"
                l = l+"\n"
                length = len(l)
                addtag( tag, offset, length )
                outlines.append( l )
                offset += length
        statmax = max( statmax, stats[0]+stats[1] )
        return filespos, tags, outlines, statmax

    def selection_changed( self, selection ):
        model, it = selection.get_selected()
        if it is None:
            return
        node, rnode = model.get(
            it, M_ID, M_NODE )
        textwidget = self.xml.get_widget( "textview_status" )
        text_buffer = textwidget.get_buffer()
        textwidget.freeze_child_notify()
        text_buffer.set_text( "" )

        try:
            self.set_revlog_header( text_buffer, node, rnode )
            eob = text_buffer.get_end_iter()
            text_buffer.insert( eob, rnode.desc+"\n\n" )
            self.filelist.clear()
            enddesc = text_buffer.get_end_iter()
            enddesc.backward_line()
            text_buffer.create_mark( "enddesc", enddesc )
            self.filelist.append( ("Content", "begdesc", None ) )
            diffmsg, buff, changes = self.repo.diff(self.repo.parents(node), node, rnode.files)
            try:
                buff = unicode( buff, "utf-8" )
            except UnicodeError:
                # XXX use a default encoding from config
                buff = unicode( buff, "iso-8859-1", 'ignore' )
            difflines = buff.splitlines()
            del buff
            eob = text_buffer.get_end_iter()
            
            offset = eob.get_offset()
            fileoffsets, tags, lines, statmax = self.prepare_diff( difflines, offset, diffmsg, changes)
            txt = u"".join(lines)

            # XXX debug : sometime gtk complains it's not valid utf-8 !!!
            text_buffer.insert( eob, txt.encode('utf-8') )

            # inserts the tags
            for name, p0, p1 in tags:
                i0 = text_buffer.get_iter_at_offset( p0 )
                i1 = text_buffer.get_iter_at_offset( p1 )
                txt = text_buffer.get_text( i0, i1 )
                text_buffer.apply_tag_by_name( name, i0, i1 )
                
            # inserts the marks
            for f, mark,offset, stats in fileoffsets:
                pos = text_buffer.get_iter_at_offset( offset )
                text_buffer.create_mark( mark, pos )
                self.filelist.append( (f, mark, (stats[0],stats[1],statmax) ) )
        finally:
            textwidget.thaw_child_notify()
        sob, eob = text_buffer.get_bounds()
        text_buffer.apply_tag_by_name( "mono", sob, eob )

    def hilight_search_string( self ):
        ##Highlight the search string on the text
        textwidget = self.xml.get_widget( "textview_status" )
        text_buffer = textwidget.get_buffer()
        if not self.find_text:
            return
        try:
            rexp = re.compile(self.find_text)
        except:
            return
        sob, eob = text_buffer.get_bounds()
        # RESTRICT TO DESCRIPTION PART : should be conditionalized
        #mark = text_buffer.get_mark( "enddesc" )
        #enddesc = text_buffer.get_iter_at_mark(mark)
        #txt = text_buffer.get_slice(sob, enddesc, True )
        txt = text_buffer.get_slice(sob, eob)
        m = rexp.search( txt )
        max_search = 50
        while m and max_search > 0: # FIXME wrong coloring in diff body
            _b = text_buffer.get_iter_at_offset( m.start() )
            _e = text_buffer.get_iter_at_offset( m.end() )
            if max_search == 50: 
                mark = text_buffer.create_mark('mark_search', _b, True)
                textwidget.scroll_to_mark(mark, .2, use_align=True, xalign=1., yalign=0.1)            
            text_buffer.apply_tag_by_name("yellowbg", _b, _e )
            m = rexp.search( txt, m.end() )
            max_search -= 1
            
    def find_entry(self):
        # text to find
        find_entry = self.xml.get_widget( "entry_find" )
        return find_entry

    def fileselection_changed( self, selection ):
        model, it = selection.get_selected()
        if it is None:
            return
        markname = model.get_value( it, 1 )
        tw = self.xml.get_widget("textview_status" )
        mark = tw.get_buffer().get_mark( markname )
        tw.scroll_to_mark( mark, .2, use_align=True, xalign=1., yalign=0. )

    def find_next_row( self, iter, stop_iter=None ):
        """Find the next revision row based on the content of
        the 'entry_find' widget"""
        txt = self.xml.get_widget( "entry_find" ).get_text()
        rexp = re.compile( txt )
        while iter != stop_iter and iter!=None:
            revnode = self.revisions.get( iter, M_NODE ) [0]
            # look in author_id, log
            author = self.repo.authors[revnode.author_id]
            if ( rexp.search( author ) or
                 rexp.search( revnode.desc ) ):
                break
            # look in diffs
            node = self.revisions.get_value(iter, M_ID)
            rnode = self.repo.read_node(node)
            buff = self.repo.single_diff(self.repo.parents(node)[0], node, rnode.files)
            if rexp.search(buff):
                break
            # look file names
            for f in revnode.files:
                if rexp.search( f ):
                    break
            else:
                iter = self.revisions.iter_next( iter )
                continue
            break
        if iter==stop_iter or iter is None:
            return None
        self.select_row( iter )
        self.hilight_search_string()
        return iter

    def select_row( self, itr ):
        if itr is None:
            self.find_text = None
            return
        else:
            self.find_text = self.xml.get_widget( "entry_find" ).get_text()

        tree = self.xml.get_widget( "treeview_revisions" )
        sel = tree.get_selection()
        sel.select_iter( itr )
        path = self.revisions.get_path( itr )
        tree.scroll_to_cell( path, use_align=True, row_align=0.2 )


    def get_selected_rev(self):
        sel = self.xml.get_widget("treeview_revisions").get_selection()
        model, it = sel.get_selected()
        if it is None:
            it = model.get_iter_first()
        return model, it

    @watch_displayed
    def on_button_find_clicked( self, *args ):
        """callback: clicking on the find button
        makes the search start at the row after the
        next row
        """
        model, it = self.get_selected_rev()
        it = self.revisions.iter_next( it )
        start_it = it
        res = self.find_next_row( it )
        if res is None:
            self.find_next_row( self.revisions.get_iter_first(), start_it )

    def on_entry_find_changed( self, *args ):
        """callback: each keypress triggers a lookup
        starting at the current row which allows the
        highlight string to grow without changing rows"""
        # DISACTIVATED for now (way too slow on medium/big repos)
        return

    def on_entry_find_activate( self, *args ):
        """Pressing enter in the entry_find field does the
        same as clicking on the Find button"""
        self.on_button_find_clicked()


    def on_filter1_activate( self, *args ):
        self.filter_dialog.show()

    def init_filter(self):
        file_filter = self.xml.get_widget("entry_file_filter")
        node_low = self.xml.get_widget("spinbutton_rev_low")
        node_high = self.xml.get_widget("spinbutton_rev_high")

        cnt = self.repo.count()
        if self.filter_files:
            file_filter.set_text( self.filerex )
        node_low.set_range(0, cnt+1 )
        node_high.set_range(0, cnt+1 )
        node_low.set_value( 0 )
        node_high.set_value( cnt )
        self.branch_selected = 'All'

    def on_button_filter_apply_clicked( self, *args ):
        file_filter = self.xml.get_widget("entry_file_filter")
        node_low = self.xml.get_widget("spinbutton_rev_low")
        node_high = self.xml.get_widget("spinbutton_rev_high")
        self.filter_files = re.compile(file_filter.get_text())
        self.filter_noderange = set(range( node_low.get_value_as_int(), node_high.get_value_as_int() ))
        self.refresh_tree()

    def on_branch_checkbox_toggled( self, *args ):
        self.on_button_filter_apply_clicked()

    def on_branch_highlight_combo_changed( self, *args ):
        self.branch_selected = self.get_selected_named_branch()
        if self.get_value_branch_checkbox():
            # if "hide others" is checked in, we really need to
            # recompute the tree
            return self.on_button_filter_apply_clicked()
        # if not, we just need to refresh to displayed part of the
        # graph to update bold lines
        tree = self.xml.get_widget( "treeview_revisions" )
        tree.queue_draw()

    def get_selected_named_branch(self):
        """
        Returns the name of the currently selected named branch in the combo
        """
        combo_filter = self.xml.get_widget("branch_highlight_combo")
        active_branch = combo_filter.get_active_text()
        return active_branch
    
    def get_value_branch_checkbox(self):
        """
        return True or False
        """
        return self.xml.get_widget("branch_checkbox").get_active()


def main():
    from hgview import __pkginfo__
    VERSION=str(__pkginfo__.numversion)
    
    parser = OptionParser(usage="%prog [-R]", version="%%prog %s" %(VERSION))
    parser.add_option( '-R', '--repository', dest='repo',
                       help='location of the repository to explore' )
    parser.add_option( '-f', '--file', dest='filename',
                       help='filter revisions which touch FILE', metavar="FILE")
    parser.add_option( '-g', '--regexp', dest='filerex',
                       help='filter revisions which touch FILE matching regexp')
    
    opt, args = parser.parse_args()
    dir_ = None
    if opt.repo:
        dir_ = opt.repo
    else:
        dir_ = os.getcwd()

    filerex = None
    if opt.filename:
        filerex = "^" + re.escape( opt.filename ) + "$"
    elif opt.filerex:
        filerex = opt.filerex

    try:
        repo = HgHLRepo( dir_ )
    except:
        print "You are not in a repo, are you ?"
        sys.exit(1)

    app = HgViewApp( repo, filerex )
    gtk.main()


if __name__ == "__main__":
    # remove current dir from sys.path
    if sys.path.count('.'):
        sys.path.remove('.')
    main()
