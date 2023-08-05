cdef extern class pywfdb.Record:
 cdef object init_record_name
 cdef object record
 cdef object basedir
 cdef int nsig
 cdef WFDB_Frequency frequency
 cdef object signal_names
 cdef WFDB_Siginfo (*siginfo)
cdef extern class pywfdb.Annotation:
 cdef object record
 cdef object basedir
 cdef WFDB_Anninfo anninfo
