cdef extern class evas.c_evas.Rect:
 cdef int x0
 cdef int y0
 cdef int x1
 cdef int y1
 cdef int cx
 cdef int cy
 cdef int _w
 cdef int _h
cdef extern class evas.c_evas.Canvas:
 cdef Evas (*obj)
cdef extern class evas.c_evas.Object:
 cdef Evas_Object (*obj)
 cdef Canvas _evas
 cdef object _data
 cdef object _callbacks
