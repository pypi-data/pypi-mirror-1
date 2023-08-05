import gtk
import gtk.gdk
import gtkimageview
import sys

try:
    pixbuf = gtk.gdk.pixbuf_new_from_file(sys.argv[1])
except IndexError:
    print 'Usage: %s image' % sys.argv[0]
    sys.exit()

view = gtkimageview.ImageView()
view.set_pixbuf(pixbuf, True)

scroll_win = gtkimageview.ImageScrollWin(view)

win = gtk.Window()
win.add(scroll_win)
win.show_all()

gtk.main()


