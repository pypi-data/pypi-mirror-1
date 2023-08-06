import gtk

notebook = gtk.Notebook()
notebook.set_scrollable(True)
notebook.popup_enable()
notebook.set_property('show-tabs', True)
notebook.set_property('homogeneous', True)
for i in range(15):
    vbox = gtk.VBox()
    notebook.append_page(vbox, gtk.Label("Tab %d" % i))
    notebook.set_tab_reorderable(vbox, True)
    #notebook.set_tab_detachable(vbox, True)

w = gtk.Window()
w.connect('delete-event', gtk.main_quit)
w.add(notebook)
w.set_size_request(600, 400)
w.show_all()
gtk.main()
