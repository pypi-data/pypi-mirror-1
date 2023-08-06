# Copyright (c) 2009-2010 Thomas Lotze
# See also LICENSE.txt

import cairo
import gtk
import gtk.gdk


class Editor(gtk.DrawingArea):

    zoom = 1
    grip = None
    viewport = None

    def __init__(self, image, cropping):
        super(Editor, self).__init__()
        self.cropping = cropping
        self.image = image
        self._scale()
        cropping.connect('changed', self.changed)
        self.connect('expose-event', self.expose)
        self.add_events(gtk.gdk.SCROLL_MASK)
        self.connect('scroll-event', self.handle_scroll)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK |
                        gtk.gdk.BUTTON1_MOTION_MASK |
                        gtk.gdk.POINTER_MOTION_MASK |
                        gtk.gdk.POINTER_MOTION_HINT_MASK)
        self.connect('button-press-event', self.handle_button_press)
        self.connect('button-release-event', self.handle_button_release)
        self.connect('motion-notify-event', self.handle_motion)

    def _scale(self):
        width, height = (int(round(self.image.get_width()*self.zoom)),
                         int(round(self.image.get_height()*self.zoom)))
        self.width, self.height = width+32, height+32
        self.set_size_request(self.width, self.height)

        self.scaled_image = cairo.ImageSurface(
            cairo.FORMAT_RGB24, width, height)
        ctx = cairo.Context(self.scaled_image)
        ctx.scale(self.zoom, self.zoom)
        ctx.set_source_surface(self.image)
        ctx.paint()

        self.shaded_image = cairo.ImageSurface(
            cairo.FORMAT_RGB24, width, height)
        ctx = cairo.Context(self.shaded_image)
        ctx.set_source_surface(self.scaled_image)
        ctx.paint_with_alpha(0.3)

    def sector(self, x, y):
        x = (x-16)/self.zoom
        y = (y-16)/self.zoom
        return ((x>=self.cropping.right) - (x<self.cropping.left),
                (y>=self.cropping.bottom) - (y<self.cropping.top))

    def changed(self, cropping):
        if self.window:
            self._repaint()

    def _repaint(self):
        self.queue_draw()
        self.window.process_updates(update_children=True)

    def expose(self, _self, event):
        ctx = self.window.cairo_create()
        ctx.paint()
        ctx.translate(16, 16)
        ctx.set_source_surface(self.shaded_image)
        ctx.paint()
        ctx.save()
        ctx.scale(self.zoom, self.zoom)
        ctx.rectangle(self.cropping.left, self.cropping.top,
                      self.cropping.width, self.cropping.height)
        ctx.restore()
        ctx.clip()
        ctx.set_source_surface(self.scaled_image)
        ctx.paint()

    def handle_scroll(self, _self, event):
        if event.direction == gtk.gdk.SCROLL_UP:
            self.zoom *= 2
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            self.zoom /= 2.
        else:
            return
        self.zoom = max(
            min(self.zoom, 1),
            1./min(self.image.get_width(), self.image.get_height()))
        self._scale()
        self._repaint()
        return True

    def handle_motion(self, _self, event):
        if event.is_hint:
            x, y, buttons = self.window.get_pointer()
        else:
            x, y = event.x, event.y
        if event.state & gtk.gdk.BUTTON1_MASK:
            ox, oy, sector = self.grip
            sx, sy = sector
            dx = int(round((x - ox)/self.zoom))
            dy = int(round((y - oy)/self.zoom))
            if sector == (0,0):
                dx = max(dx, -self.cropping.left)
                dx = min(dx, self.cropping.total_width-self.cropping.right)
                dy = max(dy, -self.cropping.top)
                dy = min(dy, self.cropping.total_height-self.cropping.bottom)
            if sx == -1 or sector == (0, 0):
                self.cropping.left += dx
            if sx == 1 or sector == (0, 0):
                self.cropping.right += dx
            if sy == -1 or sector == (0, 0):
                self.cropping.top += dy
            if sy == 1 or sector == (0, 0):
                self.cropping.bottom += dy
            self.cropping.emit('changed')
            self.grip = x, y, sector
        else:
            self.window.set_cursor(gtk.gdk.Cursor({
                (-1, -1): gtk.gdk.BOTTOM_RIGHT_CORNER,
                (-1, 0): gtk.gdk.RIGHT_SIDE,
                (-1, 1): gtk.gdk.TOP_RIGHT_CORNER,
                (0, -1): gtk.gdk.BOTTOM_SIDE,
                (0, 0): gtk.gdk.ARROW,
                (0, 1): gtk.gdk.TOP_SIDE,
                (1, -1): gtk.gdk.BOTTOM_LEFT_CORNER,
                (1, 0): gtk.gdk.LEFT_SIDE,
                (1, 1): gtk.gdk.TOP_LEFT_CORNER,
                }[self.sector(x, y)]))

    def handle_button_press(self, _self, event):
        if event.button == 1:
            sector = self.sector(event.x, event.y)
            self.grip = event.x, event.y, sector
            if sector == (0, 0):
                self.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.FLEUR))

    def handle_button_release(self, _self, event):
        if event.button == 1:
            if self.sector(event.x, event.y) == (0, 0):
                self.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.ARROW))
