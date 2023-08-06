%module sbigudrv

%{

/*
Copyright 2008 Paulo Henrique Silva <ph.silva@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

*/

#define SWIG_FILE_WITH_INIT 1
#include "sbigudrv.h"

%}

%include "numpy.i"

%init %{
  import_array();
%}

%define OBJ2LIST(type)
%typemap(out) type [ANY] {
  int i;

  $result = PyList_New($1_dim0);

  for (i = 0; i < $1_dim0; i++) {
      PyObject *obj = SWIG_NewPointerObj(&$1[i], SWIGTYPE_p_ ## type, 0);
      PyList_SetItem($result,i,obj);
  }
}
%enddef

OBJ2LIST(QUERY_USB_INFO);
OBJ2LIST(READOUT_INFO);

%typemap(in) (void* Results) {

	int res$argnum;
	if (arg1 == CC_READOUT_LINE) {
		PyArrayObject* temp=NULL;
		temp = obj_to_array_no_conversion($input,PyArray_USHORT);
		if (!temp  || !require_contiguous(temp)) SWIG_fail;
		$1 = (unsigned short*) temp->data;
	} else {
		res$argnum = SWIG_ConvertPtr($input,SWIG_as_voidptrptr(&$1), 0, 0);
		if (!SWIG_IsOK(res$argnum)) {
			SWIG_exception_fail(SWIG_ArgError(res$argnum), "in method '" "SBIGUnivDrvCommand" "', argument " "3"" of type '" "void *""'");
		}
	}
}

%include "sbigudrv.h"
