import gtk

def foo(*args):
    print "foo"

notebook = gtk.Notebook()
notebook.set_scrollable(True)
notebook.popup_enable()
notebook.set_property('show-tabs', True)
notebook.set_property('homogeneous', True)
for i in range(15):
    image = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
    eventbox = gtk.EventBox()
    eventbox.add(image)
    eventbox.connect("button-press-event", foo)
    label = gtk.Label("Tab %d" % i)
    tab = gtk.HBox()
    tab.set_spacing(0)
    tab.pack_start(label, True, True)
    tab.pack_end(eventbox, False, False)
    tab.show_all()
    vbox = gtk.VBox()
    notebook.append_page(vbox, tab)
    notebook.set_tab_reorderable(vbox, True)
    #notebook.set_tab_detachable(vbox, True)

w = gtk.Window()
w.connect('delete-event', gtk.main_quit)
w.add(notebook)
w.set_size_request(600, 400)
w.show_all()
gtk.main()
