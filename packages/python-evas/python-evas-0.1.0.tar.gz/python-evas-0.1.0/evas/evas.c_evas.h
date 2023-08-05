#ifdef __cplusplus
#define __PYX_EXTERN_C extern "C"
#else
#define __PYX_EXTERN_C extern
#endif
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasRect_Type;

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
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasCanvas_Type;

struct PyEvasCanvas {
  PyObject_HEAD
  struct __pyx_vtabstruct_4evas_6c_evas_Canvas *__pyx_vtab;
  Evas (*obj);
};
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasObject_Type;

struct PyEvasObject {
  PyObject_HEAD
  struct __pyx_vtabstruct_4evas_6c_evas_Object *__pyx_vtab;
  Evas_Object (*obj);
  struct PyEvasCanvas *_evas;
  PyObject *_data;
  PyObject *_callbacks;
};
PyMODINIT_FUNC initc_evas(void);
