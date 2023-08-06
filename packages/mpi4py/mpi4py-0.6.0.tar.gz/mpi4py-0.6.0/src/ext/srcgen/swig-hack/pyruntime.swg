%insert(runtime) %{
/* Python.h has to appear first */
#include <Python.h>
%}

%insert(runtime) "swigrun.swg";         /* SWIG API */
%insert(runtime) "swigerrors.swg";      /* SWIG errors */   
%insert(runtime) "pyhead.swg";          /* Python includes and fixes */
%insert(runtime) "pyerrors.swg";        /* Python errors */
%insert(runtime) "pythreads.swg";       /* Python thread code */
%insert(runtime) "pyapi.swg";           /* Pyton API */

%insert(runtime) %{
#if !defined(__cplusplus) && defined(__GNUC__)
/* forward declarations (GCC warns about bad prototypes) */
SWIGINTERN  PyObject *SWIG_globals(void);
SWIGRUNTIME PyObject *SWIG_Python_TypeCache(void);
#endif
%}

%insert(runtime) "pyrun.swg";           /* Python run-time code */
