#!/usr/bin/env python
from __future__ import division
import pygtk
pygtk.require('2.0')
import gtk, gtk.glade, gobject
import os, shelve


class Gasket(gobject.GObject, object):
    def __init__(self, name):
        super(Gasket, self).__init__()
        self.name = name
        self.text_buffer = gtk.TextBuffer()
        self.text_buffer.register_deserialize_tagset()
        self.text_buffer.register_serialize_tagset()

    @classmethod
    def load(cls, data):
        gaskets = []
        for v in data:
            g = cls(v["name"])
            g.load_serialized_text(v["text"])
            gaskets.append(g)
        return gaskets

    @property
    def serialized_text(self):
        # We need this because the gtk.TextBuffer can't be pickled.
        f = self.text_buffer.get_serialize_formats()[0]
        s,e = self.text_buffer.get_bounds()
        return self.text_buffer.serialize(self.text_buffer, f, s, e)

    def load_serialized_text(self, text):
        # Deserialize the text data and put it back in the TextBuffer
        f = self.text_buffer.get_deserialize_formats()[0]
        s,_ = self.text_buffer.get_bounds()
        self.text_buffer.deserialize(self.text_buffer, f, s, text)

class App(object):
    path_to_data = os.path.split(__file__)[0]
    pixmaps = {
        105 : gtk.gdk.pixbuf_new_from_file(path_to_data+"/i.png"),
        113 : gtk.gdk.pixbuf_new_from_file(path_to_data+"/q.png"),
        108 : gtk.gdk.pixbuf_new_from_file(path_to_data+"/l.png"),
        116 : gtk.gdk.pixbuf_new_from_file(path_to_data+"/t.png"),
        97  : gtk.gdk.pixbuf_new_from_file(path_to_data+"/a.png"),
    }
    def __init__(self):
        # Status bar icon.
        self.ico = gtk.status_icon_new_from_file(self.path_to_data+"/logo.svg")
        self.ico.set_visible(True)
        self.ico.connect("activate", self.activate)

        # Our persistant database that stores all of our gaskets.
        if not os.path.exists(os.environ["HOME"]+"/.gasket"):
            f1 = open(self.path_to_data+"/default.db", "r")
            f2 = open(os.environ["HOME"]+"/.gasket", "w")
            d = f1.read()
            f2.write(d)
            f1.close()
            f2.close()
        self.db = shelve.open(os.environ["HOME"]+"/.gasket")
        if self.db.has_key("gaskets_data"):
            self.gaskets_data = Gasket.load(self.db["gaskets_data"])
        else:
            self.gaskets_data = []
        self.current_gasket = None

        # Setup the glade GUI...
        self.tree = gtk.glade.XML(self.path_to_data+"/ui.glade")
        dic = {
            "quit": self.quit,
            "new_gasket": self.new_gasket,
            "start_delete": self.start_delete,
            "delete_gasket": self.delete_gasket,
            "hide": self.hide,
        }
        self.tree.signal_autoconnect(dic)

        w = self.tree.get_widget("window1")
        w.set_title("Gasket")
        w.set_icon(gtk.gdk.pixbuf_new_from_file(self.path_to_data+"/logo.svg"))

        # Setup the tree view listing all of our gaskets.
        self.gasketslist = gtk.ListStore(str, Gasket)
        self.tree.get_widget("gaskets").set_model(self.gasketslist)
        cell = gtk.CellRendererText()
        cell.set_property('editable', True)
        self.tvcolumn = gtk.TreeViewColumn('Gaskets', cell, text=0)
        self.tree.get_widget("gaskets").append_column(self.tvcolumn)

        # Make the text widget update to use the correct gasket TextBuffer when
        # the selected gasket changes on the tree view.
        self.tree.get_widget("gaskets").connect('cursor-changed',
                self.cursor_changed)

        cell.connect('edited', self.edited_gasket_name)

        # Let's make it so when the text widget is typed in it will check to see
        # if it needs to do anything special (i.e. add the icons).
        self.tree.get_widget("data").connect("key-press-event", self.key_press)

        self.populate_gasketlist()

    def populate_gasketlist(self):
        for g in self.gaskets_data:
            self.gasketslist.append([g.name, g])

        # Select the first gasket on the list.
        if self.gaskets_data:
            self.tree.get_widget("gaskets").set_cursor((0,))

    def activate(self, *args):
        """ The status bar icon was clicked (or the close button on the window).
        """
        w = self.tree.get_widget("window1")
        if w.get_property("visible"):
            w.hide()
        else:
            w.show()
        self.save()
        return True

    def hide(self, widget, event):
        widget.hide()
        if widget is self.tree.get_widget("window1"): self.save()
        return True

    def new_gasket(self, *params):
        """ Creates a new gasket. """
        g = Gasket("New Gasket")
        # A gasket may be created before most of the App is initialized.
        if hasattr(self, "gaskets_data"):
            self.gaskets_data.append(g)
            self.gasketslist.append([g.name, g])
            self.tree.get_widget("gaskets").set_cursor(
                    (len(self.gasketslist)-1,), focus_column=self.tvcolumn,
                    start_editing=True)
        return g

    def start_delete(self, *params):
        if len(self.gaskets_data) <= 1:
            # Too few!
            self.tree.get_widget("toofewdeletegasket").show()
            return
        self.tree.get_widget("deletegasket").show()

    def delete_gasket(self, *params):
        """ Deletes selected gasket. """
        self.tree.get_widget("deletegasket").hide()

        if params[1] == -8:
            self.gaskets_data.remove(self.current_gasket)
            self.gasketslist.clear()
            self.populate_gasketlist()
            self.save()

    def key_press(self, widget, event):
        """ This method checks to see if it needs to do anything special with
            input such as add an icon to the beginning of the line. """
        if event.state is gtk.gdk.MOD1_MASK and event.keyval in self.pixmaps:
            cg = self.current_gasket.text_buffer
            iter = cg.get_iter_at_offset(cg.get_property("cursor-position"))
            # Move iter to beginning of line.
            iter.set_line(iter.get_line())

            iter2 = iter.copy()
            iter2.forward_chars(1)
            # REALLY crummy way of checking to see if the first char is a pixbuf
            if len(repr(str(iter.get_slice(iter2)))) is 14:
                cg.delete(iter, iter2)

            cg.insert_pixbuf(iter, self.pixmaps[event.keyval])

    def cursor_changed(self, treeview):
        """ This updates the gui when a gasket is selected on the tree view. """
        p = self.tree.get_widget("gaskets").get_cursor()
        self.current_gasket = self.gasketslist[p[0]][1]
        self.tree.get_widget("data").set_buffer(self.current_gasket.text_buffer)
        self.save()

    def edited_gasket_name(self, cell, path, new_text):
        """ Updates the gasket name in the DB as well as the gui. """
        if new_text and new_text != self.gasketslist[path][1]:
            self.gasketslist[path][1].name = new_text
            self.gasketslist[path][0] = new_text
        self.save()

    def quit(self, *p):
        """ Exit the program. """
        self.save()
        self.db.close()
        gtk.main_quit(*p)

    def save(self):
        """ syncs the database. """
        data = []
        for g in self.gaskets_data:
            data.append({"name":g.name, "text":g.serialized_text})
        self.db["gaskets_data"] = data
        self.db.sync()

def main():
    app = App()
    gtk.main()

if __name__ == "__main__":
    main()