#ifndef __PYX_HAVE__ecore__c_ecore
#define __PYX_HAVE__ecore__c_ecore
#ifdef __cplusplus
#define __PYX_EXTERN_C extern "C"
#else
#define __PYX_EXTERN_C extern
#endif

/* "include/ecore/c_ecore.pxd":132
 * 
 * 
 * cdef public class Event [object PyEcoreEvent, type PyEcoreEvent_Type]:             # <<<<<<<<<<<<<<
 *     cdef int _set_obj(self, void *obj) except 0
 * 
 */

struct PyEcoreEvent {
  PyObject_HEAD
  struct __pyx_vtabstruct_5ecore_7c_ecore_Event *__pyx_vtab;
};

#ifndef __PYX_HAVE_API__ecore__c_ecore

__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEcoreEvent_Type;

#endif

PyMODINIT_FUNC initc_ecore(void);

#endif
