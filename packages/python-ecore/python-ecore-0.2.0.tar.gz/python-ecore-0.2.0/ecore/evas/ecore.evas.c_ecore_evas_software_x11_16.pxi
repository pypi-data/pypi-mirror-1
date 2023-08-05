# This file is included verbatim by c_ecore_evas.pyx

cdef class SoftwareX11_16(BaseX11):
    """X11 window using software render optimized for 16 bits-per-pixel.

    @ivar window: X11 window id.
    @ivar subwindow: X11 sub-window id.
    @ivar direct_resize: if direct resize is enabled or not.
    """
    def __init__(self, char *display=NULL, long parent_xid=0, int x=0, int y=0,
                 int w=320, int h=240):
        cdef Ecore_Evas *obj

        if self.obj == NULL:
            obj = ecore_evas_software_x11_16_new(display, parent_xid,
                                                 x, y, w, h)
            self._set_obj(obj)

    def window_get(self):
        """Get X11 window id.

           @rtype: int
        """
        return ecore_evas_software_x11_16_window_get(self.obj)

    property window:
        def __get__(self):
            return self.window_get()

    def subwindow_get(self):
        "@rtype: int"
        return ecore_evas_software_x11_16_subwindow_get(self.obj)

    property subwindow:
        def __get__(self):
            return self.subwindow_get()

    def direct_resize_set(self, int on):
        ecore_evas_software_x11_16_direct_resize_set(self.obj, on)

    def direct_resize_get(self):
        "@rtype: bool"
        return bool(ecore_evas_software_x11_16_direct_resize_get(self.obj))

    property direct_resize:
        def __get__(self):
            return self.direct_resize_get()

        def __set__(self, int on):
            self.direct_resize_set(on)

    def extra_event_window_add(self, long win_xid):
        ecore_evas_software_x11_16_extra_event_window_add(self.obj, win_xid)

