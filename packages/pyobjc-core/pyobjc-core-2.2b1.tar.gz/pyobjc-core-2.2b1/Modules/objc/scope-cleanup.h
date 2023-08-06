#ifndef PyObjC_SCOPE_CLEANUP_H
#define PyObjC_SCOPE_CLEANUP_H
/*
 * Defines some macro's that make cleaning up values easier.
 */

/*
 * Call Py_XDECREF() when value goes out of scope.
 *
 * Usage:
 *     PyObject* local SCOPE_DECREF = NULL;
 *
 * This is mostly equivalent to:
 *    {
 *      PyObject* lcoal = NULL;
 *
 *      ...
 *      Py_XDECREF(local);
 *    }
 *
 *  (The exception is being that SCOPE_DECREF cleans up the
 *  reference regardless of how the scope is exitted)
 */
#define SCOPE_DECREF __attribute__((__cleanup__(PyObjC_scope_decref)))

/*
 * Like SCOPE_DECREF, buf for NSObject references
 */
#define SCOPE_RELEASE	__attribute__((__cleanup__(PyOBjC_scope_release)))

/*
 * Like SCOPE_DECREF, buf for CFType references
 */
#define SCOPE_CFRELEASE	__attribute__((__cleanup__(PyOBjC_scope_cfrelease)))

static inline void PyObjC_scope_decref(PyObject** value)
{
	Py_XDECREF(*value);
	*value = NULL;
}

static inline void PyObjC_scope_release(NSObject** value)
{
	if (*value)  {
		[*value release];
	}
	*value = NULL;
}

static inline void PyObjC_scope_cfrelease(CFTypeRef* value)
{
	if (*value)  {
		CFRelease(*value);
	}
	*value = NULL;
}

#endif /* PyObjC_SCOPE_CLEANUP_H */
