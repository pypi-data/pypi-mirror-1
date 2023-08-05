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
 cdef Canvas evas
 cdef object data
 cdef object _callbacks
cdef extern class evas.c_evas.SmartObject:
 cdef object _smart_callbacks
 cdef object _m_delete
 cdef object _m_move
 cdef object _m_resize
 cdef object _m_show
 cdef object _m_hide
 cdef object _m_color_set
 cdef object _m_clip_set
 cdef object _m_clip_unset
cdef extern class evas.c_evas.Rectangle:
 pass
cdef extern class evas.c_evas.Line:
 pass
cdef extern class evas.c_evas.Image:
 pass
cdef extern class evas.c_evas.FilledImage:
 pass
cdef extern class evas.c_evas.Gradient:
 pass
cdef extern class evas.c_evas.Polygon:
 pass
cdef extern class evas.c_evas.Text:
 pass
cdef extern class evas.c_evas.ClippedSmartObject:
 cdef Rectangle clipper
