# Copyright (c) 2009 Thomas Lotze
# See also LICENSE.txt

import cairo
import gobject
import gtk


class Cropping(gobject.GObject):
    """Describes a crop area of an image that is subject to constraints.

    left, top, width, height, right, bottom: integer pixel values

    right and bottom are real coordinates of the cropping boundary, i.e. they
    count the first pixel right of and below it, analogous to Python slicing.

    """
    # aspect ratio, width, height
    # locking: setters that raise AttributeError if a value cannot be changed
    # while keeping locked values constant

    __gsignals__ = {
        'changed': (gobject.SIGNAL_RUN_LAST | gobject.SIGNAL_ACTION,
                    None, ()),
        }

    def __init__(self, total_width, total_height):
        super(Cropping, self).__init__()
        self.top = self.left = 0
        self.total_width = self.right = total_width
        self.total_height = self.bottom = total_height
        self.connect('changed', self.fix_up)

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.bottom - self.top

    @property
    def aspect_ratio(self):
        return float(self.height)/self.width

    def fix_up(self, _self):
        self.left = min(max(self.left, 0), self.total_width)
        self.right = min(max(self.right, 0), self.total_width)
        self.top = min(max(self.top, 0), self.total_height)
        self.bottom = min(max(self.bottom, 0), self.total_height)


class Rectangle(gtk.HBox):

    def __init__(self, image, cropping):
        super(Rectangle, self).__init__()
        self.pack_start(gtk.Label('Crop area: '), expand=False)
        self.display = gtk.Label()
        self.pack_end(self.display, expand=False)
        self.display.set_selectable(True)
        cropping.connect('changed', self.update)

    def update(self, cropping):
        self.display.set_text(
            '%d %d %d %d' % (cropping.left, cropping.top,
                             cropping.width, cropping.height))


class LabeledInput(gtk.VBox):

    def __init__(self, param, input):
        super(LabeledInput, self).__init__()
        label = gtk.Label(param.capitalize())
        label.set_alignment(0, 0)
        self.add(label)
        self.add(input)


class Inputs(gtk.VBox):

    def __init__(self, image, cropping):
        super(Inputs, self).__init__()

        def handle_value_changed(input, param):
            # temp fix:
            if param not in ['top', 'left', 'bottom', 'right']:
                return
            setattr(cropping, param, input.get_adjustment().value)
            cropping.emit('changed')

        self.inputs = {}
        for param in ['left', 'top', 'right', 'bottom',
                      'width', 'height', 'aspect_ratio']:
            input = self.inputs[param] = gtk.SpinButton()
            input.set_increments(1, 10)
            input.connect('value-changed', handle_value_changed, param)
            self.pack_start(LabeledInput(param, input))
        for param in ['top', 'bottom', 'height', 'aspect_ratio']:
            self.inputs[param].set_range(0, cropping.total_height)
        for param in ['left', 'right', 'width']:
            self.inputs[param].set_range(0, cropping.total_width)
        self.inputs['aspect_ratio'].set_digits(5)
        self.inputs['aspect_ratio'].set_increments(0.1, 1)

        cropping.connect('changed', self.update)
        self.update(cropping)

    def update(self, cropping):
        for param in self.inputs:
            self.inputs[param].set_value(getattr(cropping, param))


class Preview(gtk.DrawingArea):

    def __init__(self, image, cropping):
        super(Preview, self).__init__()
        cropping.connect('changed', self.update, image)
        self.connect('expose_event', self.expose)
        self.set_size_request(200, 200)
        self.update(cropping, image)

    def update(self, cropping, image):
        if cropping.width <= 200 and cropping.height <= 200:
            scale = 1
            self.width = cropping.width
            self.height = cropping.height
        elif cropping.width >= cropping.height:
            scale = 200./cropping.width
            self.width = 200
            self.height = int(round(cropping.height * scale))
        else:
            scale = 200./cropping.height
            self.height = 200
            self.width = int(round(cropping.width * scale))

        self.cropped_image = cairo.ImageSurface(
            cairo.FORMAT_RGB24, self.width, self.height)
        ctx = cairo.Context(self.cropped_image)
        ctx.scale(scale, scale)
        ctx.translate(-cropping.left, -cropping.top)
        ctx.set_source_surface(image)
        ctx.paint()

        if not self.window:
            return

        self.queue_draw()
        self.window.process_updates(update_children=True)

    def expose(self, _self, event):
        ctx = self.window.cairo_create()
        ctx.set_source_rgba(0, 0, 0, 0)
        ctx.paint()
        ctx.set_source_surface(
                self.cropped_image, (200-self.width)/2, (200-self.height)/2)
        ctx.paint()


class Masked(gtk.DrawingArea):

    def __init__(self, image, cropping):
        super(Masked, self).__init__()
        cropping.connect('changed', self.changed)
        self.connect('expose_event', self.expose, cropping)

        self.scale = 200./max(cropping.total_width, cropping.total_height)
        if cropping.total_width >= cropping.total_height:
            self.width = 200
            self.height = int(round(self.scale*cropping.total_height))
        else:
            self.width = int(round(self.scale*cropping.total_width))
            self.height = 200
        self.set_size_request(200, self.height)

        self.scaled_image = cairo.ImageSurface(
            cairo.FORMAT_RGB24, self.width, self.height)
        ctx = cairo.Context(self.scaled_image)
        ctx.scale(self.scale, self.scale)
        ctx.set_source_surface(image, 0, 0)
        ctx.paint()

        self.shaded_image = cairo.ImageSurface(
            cairo.FORMAT_RGB24, self.width, self.height)
        ctx = cairo.Context(self.shaded_image)
        ctx.set_source_surface(self.scaled_image)
        ctx.paint_with_alpha(0.3)

    def changed(self, cropping):
        self.queue_draw()
        self.window.process_updates(update_children=True)

    def expose(self, _self, event, cropping):
        ctx = self.window.cairo_create()
        ctx.translate((200-self.width)/2, 0)
        ctx.set_source_surface(self.shaded_image)
        ctx.paint()
        ctx.rectangle(cropping.left*self.scale, cropping.top*self.scale,
                      cropping.width*self.scale, cropping.height*self.scale)
        ctx.clip()
        ctx.set_source_surface(self.scaled_image)
        ctx.paint()


class Sidebar(gtk.VBox):

    widget_factories = [
        Rectangle,
        Inputs,
        Preview,
        Masked,
        ]

    def __init__(self, image, cropping):
        super(Sidebar, self).__init__()

        for factory in self.widget_factories:
            self.pack_start(factory(image, cropping),
                            expand=True, fill=False, padding=5)
