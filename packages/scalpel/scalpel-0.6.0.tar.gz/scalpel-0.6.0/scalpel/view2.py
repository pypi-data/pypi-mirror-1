import gtk 
import cairo 
from math import sin

class Model(object):
    def __init__(self):
        self.start = 0
        self.length = 0

    def values(self):
        x1, x2 = int(self.start), int(self.start + self.length)
        return [sin(x / 100.) for x in range(x1, x2)]


class View(gtk.DrawingArea):

    __gsignals__ = {"expose-event": "override"}

    def __init__(self, model):
        super(View, self).__init__()
        self._model = model
        self._cache = None
        self.connect("size_allocate", self.resized)

    def resized(self, widget, rect):
        self._model.length = rect.width
        self.redraw()
    
    def do_expose_event(self, event):
        context = self.window.cairo_create()
        context.rectangle(event.area.x, event.area.y,
                          event.area.width, event.area.height)
        context.clip()
        width, height = self.window.get_size()
        self.draw(context, width, height)

    def redraw(self):
        # queue_draw() emits an expose event. Double buffering is used
        # automatically in the expose event handler.
        self._cache = None
        self.queue_draw()

    def draw(self, context, width, height):
        if self._cache is None:
            surface = context.get_target()
            self._cache = surface.create_similar(cairo.CONTENT_COLOR,
                                                 width, height)
            c = cairo.Context(self._cache)

            # Black background
            c.set_source_rgb(0, 0, 0)
            c.paint()

            c.set_source_rgb(0.0, 0.47058823529411764, 1.0)
            values = self._model.values()
            for i, v in enumerate(values):
                # Fill one pixel 
                x = i
                y = int((v * 0.5 + 0.5) * height)
                c.rectangle(x, y, 1, 1)
                c.fill()

        context.set_source_surface(self._cache, 0, 0)
        context.set_operator(cairo.OPERATOR_SOURCE)
        context.paint()


class Controller(object):
    def __init__(self, view, model):
        self.model = model
        self.pressed = False
        view.add_events(gtk.gdk.BUTTON_PRESS_MASK |
                          gtk.gdk.BUTTON_RELEASE_MASK |
                          gtk.gdk.POINTER_MOTION_MASK |
                          gtk.gdk.POINTER_MOTION_HINT_MASK)
        view.connect("button_press_event", self.button_press)
        view.connect("button_release_event", self.button_release)
        view.connect("motion_notify_event", self.motion_notify)

    def button_press(self, view, event):
        if event.button == 1:
            self.pressed = True
            self._xlast = event.x

    def button_release(self, view, event):
        if event.button == 1:
            self.pressed = False

    def motion_notify(self, view, event):
        if self.pressed:
            x = event.window.get_pointer()[0]
            delta = self._xlast - x
            self._xlast = x
            self.model.start += delta 
            view.redraw()
    

if __name__ == '__main__':
    model = Model()
    view = View(model)
    controller = Controller(view, model)
    w = gtk.Window()
    w.connect("delete-event", gtk.main_quit)
    w.add(view)
    w.resize(700, 500)
    w.show_all()
    gtk.main()
