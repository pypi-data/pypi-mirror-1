#ifndef __PYX_HAVE__evas__c_evas
#define __PYX_HAVE__evas__c_evas
#ifdef __cplusplus
#define __PYX_EXTERN_C extern "C"
#else
#define __PYX_EXTERN_C extern
#endif

/* "include/evas/c_evas.pxd":585
 * 
 * 
 * cdef public class Rect [object PyEvasRect, type PyEvasRect_Type]:             # <<<<<<<<<<<<<<
 *     cdef int x0, y0, x1, y1, cx, cy, _w, _h
 * 
 */

struct PyEvasRect {
  PyObject_HEAD
  int x0;
  int y0;
  int x1;
  int y1;
  int cx;
  int cy;
  int _w;
  int _h;
};

/* "include/evas/c_evas.pxd":684
 * 
 * 
 * cdef public class Canvas [object PyEvasCanvas, type PyEvasCanvas_Type]:             # <<<<<<<<<<<<<<
 *     cdef Evas *obj
 * 
 */

struct PyEvasCanvas {
  PyObject_HEAD
  struct __pyx_vtabstruct_4evas_6c_evas_Canvas *__pyx_vtab;
  Evas *obj;
};

/* "include/evas/c_evas.pxd":691
 * 
 * 
 * cdef public class Object [object PyEvasObject, type PyEvasObject_Type]:             # <<<<<<<<<<<<<<
 *     cdef Evas_Object *obj
 *     cdef readonly Canvas evas
 */

struct PyEvasObject {
  PyObject_HEAD
  struct __pyx_vtabstruct_4evas_6c_evas_Object *__pyx_vtab;
  Evas_Object *obj;
  struct PyEvasCanvas *evas;
  PyObject *data;
  PyObject *_callbacks;
};

/* "include/evas/c_evas.pxd":701
 * 
 * 
 * cdef public class SmartObject(Object) [object PyEvasSmartObject,             # <<<<<<<<<<<<<<
 *                                        type PyEvasSmartObject_Type]:
 *     cdef object _smart_callbacks
 */

struct PyEvasSmartObject {
  struct PyEvasObject __pyx_base;
  PyObject *_smart_callbacks;
  PyObject *_m_delete;
  PyObject *_m_move;
  PyObject *_m_resize;
  PyObject *_m_show;
  PyObject *_m_hide;
  PyObject *_m_color_set;
  PyObject *_m_clip_set;
  PyObject *_m_clip_unset;
};

/* "include/evas/c_evas.pxd":714
 * 
 * 
 * cdef public class Rectangle(Object) [object PyEvasRectangle,             # <<<<<<<<<<<<<<
 *                                      type PyEvasRectangle_Type]:
 *     pass
 */

struct PyEvasRectangle {
  struct PyEvasObject __pyx_base;
};

/* "include/evas/c_evas.pxd":719
 * 
 * 
 * cdef public class Line(Object) [object PyEvasLine, type PyEvasLine_Type]:             # <<<<<<<<<<<<<<
 *     pass
 * 
 */

struct PyEvasLine {
  struct PyEvasObject __pyx_base;
};

/* "include/evas/c_evas.pxd":723
 * 
 * 
 * cdef public class Image(Object) [object PyEvasImage, type PyEvasImage_Type]:             # <<<<<<<<<<<<<<
 *     pass
 * 
 */

struct PyEvasImage {
  struct PyEvasObject __pyx_base;
};

/* "include/evas/c_evas.pxd":727
 * 
 * 
 * cdef public class FilledImage(Image) [object PyEvasFilledImage,             # <<<<<<<<<<<<<<
 *                                       type PyEvasFilledImage_Type]:
 *     pass
 */

struct PyEvasFilledImage {
  struct PyEvasImage __pyx_base;
};

/* "include/evas/c_evas.pxd":732
 * 
 * 
 * cdef public class Gradient(Object) [object PyEvasGradient,             # <<<<<<<<<<<<<<
 *                                     type PyEvasGradient_Type]:
 *     pass
 */

struct PyEvasGradient {
  struct PyEvasObject __pyx_base;
};

/* "include/evas/c_evas.pxd":737
 * 
 * 
 * cdef public class Polygon(Object) [object PyEvasPolygon,             # <<<<<<<<<<<<<<
 *                                    type PyEvasPolygon_Type]:
 *     pass
 */

struct PyEvasPolygon {
  struct PyEvasObject __pyx_base;
};

/* "include/evas/c_evas.pxd":742
 * 
 * 
 * cdef public class Text(Object) [object PyEvasText, type PyEvasText_Type]:             # <<<<<<<<<<<<<<
 *     pass
 * 
 */

struct PyEvasText {
  struct PyEvasObject __pyx_base;
};

/* "include/evas/c_evas.pxd":746
 * 
 * 
 * cdef public class ClippedSmartObject(SmartObject) \             # <<<<<<<<<<<<<<
 *          [object PyEvasClippedSmartObject, type PyEvasClippedSmartObject_Type]:
 *     cdef readonly Rectangle clipper
 */

struct PyEvasClippedSmartObject {
  struct PyEvasSmartObject __pyx_base;
  struct PyEvasRectangle *clipper;
};

#ifndef __PYX_HAVE_API__evas__c_evas

__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasRect_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasCanvas_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasObject_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasSmartObject_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasRectangle_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasLine_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasImage_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasFilledImage_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasGradient_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasPolygon_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasText_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasClippedSmartObject_Type;

#endif

PyMODINIT_FUNC initc_evas(void);

#endif
