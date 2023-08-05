extern DL_IMPORT(PyTypeObject) RecordType;

struct PyRecord {
  PyObject_HEAD
  struct __pyx_vtabstruct_6pywfdb_Record *__pyx_vtab;
  PyObject *init_record_name;
  PyObject *record;
  PyObject *basedir;
  int nsig;
  WFDB_Frequency frequency;
  PyObject *signal_names;
  WFDB_Siginfo (*siginfo);
};
extern DL_IMPORT(PyTypeObject) AnnotationType;

struct PyAnnotation {
  PyObject_HEAD
  PyObject *record;
  PyObject *basedir;
  WFDB_Anninfo anninfo;
};
extern DL_IMPORT(void) initpywfdb(void);
