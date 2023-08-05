#ifndef __PYX_HAVE__evas__c_evas
#define __PYX_HAVE__evas__c_evas
#ifdef __cplusplus
#define __PYX_EXTERN_C extern "C"
#else
#define __PYX_EXTERN_C extern
#endif

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

struct PyEvasCanvas {
  PyObject_HEAD
  struct __pyx_vtabstruct_4evas_6c_evas_Canvas *__pyx_vtab;
  Evas *obj;
};

struct PyEvasObject {
  PyObject_HEAD
  struct __pyx_vtabstruct_4evas_6c_evas_Object *__pyx_vtab;
  Evas_Object *obj;
  struct PyEvasCanvas *evas;
  PyObject *data;
  PyObject *_callbacks;
};

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

struct PyEvasRectangle {
  struct PyEvasObject __pyx_base;
};

struct PyEvasLine {
  struct PyEvasObject __pyx_base;
};

struct PyEvasImage {
  struct PyEvasObject __pyx_base;
};

struct PyEvasFilledImage {
  struct PyEvasImage __pyx_base;
};

struct PyEvasGradient {
  struct PyEvasObject __pyx_base;
};

struct PyEvasPolygon {
  struct PyEvasObject __pyx_base;
};

struct PyEvasText {
  struct PyEvasObject __pyx_base;
};

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
