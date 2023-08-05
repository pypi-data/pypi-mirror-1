# This file is included verbatim by c_ecore.pyx

import traceback

cdef int idler_cb(void *_td) with gil:
    cdef Idler obj
    cdef int r

    obj = <Idler>_td

    try:
        r = bool(obj._exec())
    except Exception, e:
        traceback.print_exc()
        r = 0

    if not r:
        obj.delete()
    return r


cdef class Idler:
    """Add an idler handler.

       This class represents an idler on the event loop that will
       call B{func} when there is nothing more to do. The function will
       be passed any extra parameters given to constructor.

       When the idler B{func} is called, it must return a value of either
       True or False (remember that Python returns None if no value is
       explicitly returned and None evaluates to False). If it returns
       B{True}, it will be called again when system become idle, or if it
       returns B{False} it will be deleted automatically making any
       references/handles for it invalid.

       Idlers should be stopped/deleted by means of L{delete()} or
       returning False from B{func}, otherwise they'll continue alive, even
       if the current python context delete it's reference to it.

       Idlers are useful for progressively prossessing data without blocking.
    """
    def __init__(self, func, *args, **kargs):
        self.func = func
        self.args = args
        self.kargs = kargs
        if self.obj == NULL:
            self.obj = ecore_idler_add(idler_cb, <void *>self)
            if self.obj != NULL:
                python.Py_INCREF(self)

    def __str__(self):
        return "%s(func=%s, args=%s, kargs=%s)" % \
               (self.__class__.__name__, self.func, self.args, self.kargs)

    def __repr__(self):
        return ("%s(0x%x, func=%s, args=%s, kargs=%s, Ecore_Idler=0x%x, "
                "refcount=%d)") % \
               (self.__class__.__name__, <unsigned long>self,
                self.func, self.args, self.kargs,
                <unsigned long>self.obj, PY_REFCOUNT(self))

    def __dealloc__(self):
        if self.obj != NULL:
            ecore_idler_del(self.obj)
            self.obj = NULL
        self.func = None
        self.args = None
        self.kargs = None

    cdef object _exec(self):
        return self.func(*self.args, **self.kargs)

    def delete(self):
        "Stop callback emission and free internal resources."
        if self.obj != NULL:
            ecore_idler_del(self.obj)
            self.obj = NULL
            python.Py_DECREF(self)

    def stop(self):
        "Alias for L{delete()}."
        self.delete()


def idler_add(func, *args, **kargs):
    """L{Idler} factory, for C-api compatibility.

       @rtype: L{Idler}
    """
    return Idler(func, *args, **kargs)
