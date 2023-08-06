# Copyright (c) 2009 Thomas Lotze
# See also LICENSE.txt

import cairo
import gobject
import gtk
import gtk.gdk
import gtk.keysyms
import os.path
import sys
import tl.gcrop.cropping
import tl.gcrop.edit


class GCropWindow(gtk.Window):

    __gsignals__ = {
        'open': (gobject.SIGNAL_RUN_LAST | gobject.SIGNAL_ACTION,
                 None, ()),
        }

    image = None
    cropping = None

    def __init__(self):
        super(GCropWindow, self).__init__(gtk.WINDOW_TOPLEVEL)
        self.set_default_size(640, 480)
        self.connect('delete-event', gtk.main_quit)

        self.file_chooser = gtk.FileChooserDialog(
            title=u'Open an image',
            buttons=('Open', gtk.RESPONSE_APPLY))
        self.connect('open', self.handle_open)

    def handle_open(self, _self):
        if self.file_chooser.run() == gtk.RESPONSE_APPLY:
            self.open(self.file_chooser.get_filename())
        self.file_chooser.hide()

    def open(self, filename):
        pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
        width = pixbuf.get_width()
        height = pixbuf.get_height()

        self.image = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
        ctx = gtk.gdk.CairoContext(cairo.Context(self.image))
        ctx.set_source_pixbuf(pixbuf, 0, 0)
        ctx.paint()

        self.cropping = tl.gcrop.cropping.Cropping(width, height)

        self.set_title('%s (%s x %s)' % (os.path.basename(filename),
                                         width, height))
        if self.child:
            self.remove(self.child)
        hbox = gtk.HBox()
        self.add(hbox)

        scrolled = gtk.ScrolledWindow()
        hbox.pack_start(scrolled)
        editor = tl.gcrop.edit.Editor(self.image, self.cropping)
        scrolled.add_with_viewport(editor)
        editor.viewport = scrolled.child

        hbox.pack_end(tl.gcrop.cropping.Sidebar(self.image, self.cropping),
                      expand=False, fill=False, padding=5)

        hbox.show_all()


gtk.binding_entry_add_signal(
    GCropWindow, gtk.keysyms.o, gtk.gdk.CONTROL_MASK, 'open')


def gcrop():
    window = GCropWindow()
    window.show_all()
    if len(sys.argv) > 1:
        window.open(sys.argv[1])
    else:
        window.emit('open')
    gtk.main()
