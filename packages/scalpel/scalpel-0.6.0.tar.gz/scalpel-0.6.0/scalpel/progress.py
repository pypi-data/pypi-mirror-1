import gtk
from cursor import Repeat
gtk.gdk.threads_init()


class Progress(object):

    def __init__(self):
        p = gtk.ProgressBar()
        p.set_text("Loading ...")
        w = gtk.Dialog(title="Loading", 
                       parent=None, 
                       #flags = gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                       buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        w.vbox.add(p)
        w.connect('delete-event', quit)
        w.show_all()

        self.p = p
        self.w = w

    def start(self):
        def foo():
            gtk.gdk.threads_enter()
            self.p.pulse()
            while gtk.events_pending():
               gtk.main_iteration(False)
            gtk.gdk.threads_leave()
        r = Repeat(foo, 0.2)
        r.start()
        self.r = r

    def stop(self):
        self.r.stop()
        print "stopped"
        gtk.gdk.threads_enter()
        self.w.destroy()
        gtk.gdk.threads_leave()
            

if __name__ == '__main__':
    p = Progress()
    p.start()
    gtk.main()
    
