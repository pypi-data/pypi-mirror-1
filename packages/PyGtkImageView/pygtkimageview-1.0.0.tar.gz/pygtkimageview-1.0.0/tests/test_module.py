import gobject
import gtk
import gtk.gdk
import gtkimageview

def test_version_string():
    '''
    The module has a __version__ attribute which is a string
    containing three numbers separted by periods. The version string
    is >= 1.0.0.
    '''
    major, minor, micro = gtkimageview.__version__.split('.')
    major, minor, micro = int(major), int(minor), int(micro)
    assert major >= 1
    if major == 1:
        assert minor >= 0

def test_default_tool():
    '''
    The default tool is ImageToolDragger.
    '''
    view = gtkimageview.ImageView()
    assert isinstance(view.get_tool(), gtkimageview.ImageToolDragger)

def test_set_wrong_pixbuf_type():
    '''
    A TypeError is raised when set_pixbuf() is called with something
    that is not a pixbuf.
    '''
    view = gtkimageview.ImageView()
    try:
        view.set_pixbuf('Hi mom!', True)
        assert False
    except TypeError:
        assert True

def set_pixbuf_null():
    view = gtkimageview.ImageView()
    view.set_pixbuf(None, True)
    assert not view.get_pixbuf()

def test_set_pixbuf_default():
    '''
    Make sure that set_pixbuf():s second parameter has the default
    value True.
    '''
    view = gtkimageview.ImageView()
    view.set_fitting(False)
    view.set_pixbuf(None)
    assert view.get_fitting()

def check_class(parent, init_args):
    class TheClass(parent):
        __gsignals__ = {'my-signal' : (gobject.SIGNAL_RUN_FIRST,
                                       gobject.TYPE_NONE,
                                       (gobject.TYPE_INT,))}
        def __init__(self):
            parent.__init__(self, *init_args)
            self.arg = 0
        def do_my_signal(self, arg):
            self.arg = arg
    gobject.type_register(TheClass)
    obj = TheClass()
    obj.emit('my-signal', 20)
    assert obj.arg == 20

def test_nav_subclass_with_signals():
    '''
    Ensure that a subclass of ImageNav which adds a signal to the
    class works as expected.
    '''
    check_class(gtkimageview.ImageNav, [gtkimageview.ImageView()])

def test_view_subclass_with_signals():
    '''
    Ensure that a subclass of ImageView which adds a signal to the
    class works as expected.
    '''
    check_class(gtkimageview.ImageView, [])

def test_selector_subclass_with_signals():
    '''
    Ensure that a subclass of ImageToolSelector which adds a signal to
    the class works as expected.
    '''
    check_class(gtkimageview.ImageToolSelector, [gtkimageview.ImageView()])

def test_dragger_subclass_with_signals():
    '''
    Ensure that a subclass of ImageToolDragger which adds a signal to
    the class works as expected.
    '''
    check_class(gtkimageview.ImageToolDragger, [gtkimageview.ImageView()])

def test_scroll_win_subclass_with_signals():
    '''
    Ensure that a subclass of ImageScrollWin which adds a signal to
    the class works as expected.
    '''
    check_class(gtkimageview.ImageScrollWin, [gtkimageview.ImageView()])

def test_min_max_zoom_functions():
    '''
    Ensure that the gtkimageview.zooms_* functions are present and
    works as expected.
    '''
    min_zoom = float(gtkimageview.zooms_get_min_zoom())
    max_zoom = float(gtkimageview.zooms_get_max_zoom())
    assert min_zoom < max_zoom

def test_get_viewport():
    '''
    Ensure that getting the viewport of the view works as expected.
    '''
    view = gtkimageview.ImageView()
    assert not view.get_viewport()

    view.size_allocate(gtk.gdk.Rectangle(0, 0, 100, 100))
    pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 50, 50)
    view.set_pixbuf(pixbuf)

    rect = view.get_viewport()
    assert rect.x == 0 and rect.y == 0
    assert rect.width == 50 and rect.height == 50

def test_get_check_colors():
    '''
    Ensure that getting the view:s check colors works as expected.
    '''
    view = gtkimageview.ImageView()
    col1, col2 = view.get_check_colors()
    assert int(col1)
    assert int(col2)

def test_get_check_colors_many_args():
    '''
    Ensure that a correct error is thrown when get_check_colors() is
    invoked with to many arguments.
    '''
    view = gtkimageview.ImageView()
    try:
        view.get_check_colors(1, 2, 3)
        assert False
    except TypeError:
        assert True

def test_image_nav_wrong_nr_args():
    '''
    Ensure that TypeError is raised when ImageNav is instantiated with
    the wrong nr of args.
    '''
    try:
        nav = gtkimageview.ImageNav()
        assert False
    except TypeError:
        assert True
    try:
        nav = gtkimageview.ImageNav(gtkimageview.ImageView(), None, None)
        assert False
    except TypeError:
        assert True

def test_get_draw_rect():
    '''
    Ensure that getting the draw rectangle works as expected.
    '''
    view = gtkimageview.ImageView()
    assert not view.get_draw_rect()

    view.size_allocate(gtk.gdk.Rectangle(0, 0, 100, 100))
    pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 50, 50)
    view.set_pixbuf(pixbuf)

    rect = view.get_draw_rect()
    assert rect.x == 25 and rect.y == 25
    assert rect.width == 50 and rect.height == 50

def test_set_offset():
    '''
    Ensure that setting the offset works as expected.
    '''
    view = gtkimageview.ImageView()
    view.size_allocate(gtk.gdk.Rectangle(0, 0, 100, 100))
    pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 200, 200)
    view.set_pixbuf(pixbuf)
    view.set_zoom(1)

    view.set_offset(0, 0)
    rect = view.get_viewport()
    assert rect.x == 0 and rect.y == 0

    view.set_offset(100, 100, invalidate = True)
    rect = view.get_viewport()
    assert rect.x == 100 and rect.y == 100
    
def test_set_transp():
    '''
    Ensure that setting the views transparency settings works as
    expected.
    '''
    view = gtkimageview.ImageView()
    view.set_transp(gtkimageview.TRANSP_COLOR, transp_color = 0xff0000)
    col1, col2 = view.get_check_colors()
    assert col1 == col2 == 0xff0000
    
    view.set_transp(gtkimageview.TRANSP_GRID)
    
    
