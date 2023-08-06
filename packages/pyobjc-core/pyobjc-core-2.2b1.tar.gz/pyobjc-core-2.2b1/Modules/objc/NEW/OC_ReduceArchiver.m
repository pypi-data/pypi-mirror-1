/*
 * Implementation of an NSCoder that can be used for pickling Cocoa objects
 */
#include "pyobjc.h"

PyObject* PyObjC_recoverArchiveFunc = NULL;


@implementation OC_PickeArchiver

+newWithRootObject:(NSObject<NSCoding>*)object
{
	return [[[self alloc] initWithRootObject:object] autorelease];
}

-initWithRootObject:(NSObject<NSCoding>*)object
{
	object = [object replacementObjectForCoder:self];
	className = class_getName([object classForCoder]);
	classVersion = [[object class] version];
	attributes = NULL;

	PyObjC_BEGIN_WITH_GIL
		keyedAttributes = PyDict_New();
		if (keyedAttributes == NULL) {
			PyObjC_GIL_FORWARD_EXC();
		}
		attributes = PyList_New(0);
		if (attributes == NULL) {
			PyObjC_GIL_FORWARD_EXC();
		}

	PyObjC_END_WITH_GIL

	[object encodeWithCoder:self];

	return self;
}

-(void)dealloc
{
	PyObjC_BEGIN_WITH_GIL
		Py_XDECREF(keyedAttributes);
		Py_XDECREF(attributes);

	PyObjC_END_WITH_GIL

	[super dealloc];
}

-(PyObject*)state
{
	PyObject* result;

	PyObjC_BEGIN_WITH_GIL
		 result = Py_BuildValue("O(sIiOO)",
			PyObjC_recoverArchiveFunc, 
			className, [self systemVersion], classVersion,
			keyedAttributes, attributes);
	PyObjC_END_WITH_GIL

	return result;
}

/* Implementation for the actual coding protocol starts here */

-(BOOL)allowsKeyedCoding
{	
	return YES;
}



-(void)encodeBool:(BOOL)val forKey:(NSString*)key
{
static  char encoding[] = { _C_NSBOOL, 0 };

	PyObjC_BEGIN_WITH_GIL
		PyObject* pkey = PyObjC_IdToPython(key);
		if (pkey == NULL) {
			PyObjC_GIL_FORWARD_EXC();
		}

		PyObject* pval = pythonify_c_value(encoding, &val);
		if (pval == NULL) {
			PyObjC_GIL_FORWARD_EXC();
		}

		int r = PyDict_SetItem(keyedAttributes, pkey, pval);
		if (r == -1) {
			PyObjC_GIL_FORWARD_EXC();
		}

		Py_DECREF(pkey);
		Py_DECREF(pval);
	
	PyObjC_END_WITH_GIL
}

-(void)encodeBytes:(const uint8_t*)buf length:(NSUInteger)len forKey:(NSString*)key
{
	PyObjC_BEGIN_WITH_GIL
		PyObject* pkey = PyObjC_IdToPython(key);
		if (pkey == NULL) {
			PyObjC_GIL_FORWARD_EXC();
		}

		PyObject* pval = PyString_FromStringAndSize((char*)buf, (Py_ssize_t)len);
		if (pval == NULL) {
			PyObjC_GIL_FORWARD_EXC();
		}

		int r = PyDict_SetItem(keyedAttributes, pkey, pval);
		if (r == -1) {
			PyObjC_GIL_FORWARD_EXC();
		}
		
		Py_DECREF(pkey);
		Py_DECREF(pval);
	
	PyObjC_END_WITH_GIL
}
#define VALUE_KEYED_ENCODE(type)  \
	PyObjC_BEGIN_WITH_GIL						\
		PyObject* pkey = PyObjC_IdToPython(key);		\
		if (pkey == NULL) {					\
			PyObjC_GIL_FORWARD_EXC();			\
		}							\
									\
		PyObject* pval = pythonify_c_value(@encode(type), &val);\
		if (pval == NULL) {					\
			PyObjC_GIL_FORWARD_EXC();			\
		}							\
									\
		int r = PyDict_SetItem(keyedAttributes, pkey, pval);	\
		if (r == -1) {						\
			PyObjC_GIL_FORWARD_EXC();			\
		}							\
									\
		Py_DECREF(pkey);					\
		Py_DECREF(pval);					\
									\
	PyObjC_END_WITH_GIL

-(void)encodeDouble:(double)val forKey:(NSString*)key
{
	VALUE_KEYED_ENCODE(double)
}

-(void)encodeFloat:(float)val forKey:(NSString*)key
{
	VALUE_KEYED_ENCODE(float)
}

-(void)encodeInt32:(int32_t)val forKey:(NSString*)key
{
	VALUE_KEYED_ENCODE(int32_t)
}

-(void)encodeInt64:(int64_t)val forKey:(NSString*)key
{
	VALUE_KEYED_ENCODE(int64_t)
}

-(void)encodeInt:(int)val forKey:(NSString*)key
{
	VALUE_KEYED_ENCODE(int)
}

-(void)encodeInteger:(NSInteger)val forKey:(NSString*)key
{
	VALUE_KEYED_ENCODE(NSInteger)
}

-(void)encodeObject:(id)val forKey:(NSString*)key
{
	VALUE_KEYED_ENCODE(id)
}

-(void)encodePoint:(NSPoint)val forKey:(NSString*)key
{
	VALUE_KEYED_ENCODE(NSPoint)
}

-(void)encodeRect:(NSRect)val forKey:(NSString*)key
{
	VALUE_KEYED_ENCODE(NSRect)
}

-(void)encodeSize:(NSSize)val forKey:(NSString*)key
{
	VALUE_KEYED_ENCODE(NSSize)
}


#define VALUE_ENCODE(type)  \
	PyObjC_BEGIN_WITH_GIL						\
									\
		PyObject* pval = pythonify_c_value(@encode(type), &val);\
		if (pval == NULL) {					\
			PyObjC_GIL_FORWARD_EXC();			\
		}							\
									\
		int r = PyList_Append(attributes, pval);	\
		if (r == -1) {						\
			PyObjC_GIL_FORWARD_EXC();			\
		}							\
									\
		Py_DECREF(pval);					\
									\
	PyObjC_END_WITH_GIL


-(void)encodeBytes:(const uint8_t*)buf length:(NSUInteger)len
{
	PyObjC_BEGIN_WITH_GIL
		PyObject* pval = PyString_FromStringAndSize((char*)buf, (Py_ssize_t)len);
		if (pval == NULL) {
			PyObjC_GIL_FORWARD_EXC();
		}

		int r = PyList_Append(attributes, pval);
		if (r == -1) {
			PyObjC_GIL_FORWARD_EXC();
		}
		
		Py_DECREF(pval);
	
	PyObjC_END_WITH_GIL
}

-(void)encodeObject:(id)val
{
	VALUE_ENCODE(id)
}

-(void)encodeValueOfObjCType:(const char*)type at:(const void*)addr
{
	PyObjC_BEGIN_WITH_GIL						
									
		PyObject* pval = pythonify_c_value(type, (void*)addr);
		if (pval == NULL) {					
			PyObjC_GIL_FORWARD_EXC();			
		}						
									
		int r = PyList_Append(attributes, pval);	
		if (r == -1) {						
			PyObjC_GIL_FORWARD_EXC();			
		}							
									
		Py_DECREF(pval);					
									
	PyObjC_END_WITH_GIL
}

-(void)encodeDataObject:(NSData*)data
{
	[self encodeBytes:[data bytes] length:[data length]];
}


@end


@implementation OC_PickleUnarchiver

+newWithState:(PyObject*)state
{
	return [[[self alloc] initWithState:state] autorelease];
}

-initWithState:(PyObject*)state
{
	Class aClass = nil;

	PyObjC_BEGIN_WITH_GIL
		attributeIndex = 0;

		if (!PyTuple_Check(state) && PyTuple_GET_SIZE(state) != 4) {
			PyObjC_GIL_FORWARD_EXC();	
		}

		keyedAttributes = PyTuple_GET_ITEM(state, 3);
		Py_INCREF(keyedAttributes);
		attributes = PyTuple_GET_ITEM(state, 4);
		Py_INCREF(attributes);

		if (PyInt_Check(PyTuple_GET_ITEM(state, 1))) {
			systemVersion = (unsigned)PyInt_AsLong(
			PyTuple_GET_ITEM(state, 1));
		} else if (PyLong_Check(PyTuple_GET_ITEM(state, 1))) {
			systemVersion = (unsigned)PyLong_AsLong(
			PyTuple_GET_ITEM(state, 1));
		} else {
			PyErr_SetString(PyExc_ValueError,
					"bad pickle state");
			PyObjC_GIL_FORWARD_EXC();
		}

		if (PyInt_Check(PyTuple_GET_ITEM(state, 2))) {
			classVersion = (unsigned)PyInt_AsLong(
			PyTuple_GET_ITEM(state, 2));
		} else if (PyLong_Check(PyTuple_GET_ITEM(state, 2))) {
			classVersion = (unsigned)PyLong_AsLong(
			PyTuple_GET_ITEM(state, 2));
		} else {
			PyErr_SetString(PyExc_ValueError,
					"bad pickle state");
			PyObjC_GIL_FORWARD_EXC();
		}

		if (!PyString_Check(PyTuple_GET_ITEM(state, 0))) {
			PyErr_SetString(PyExc_ValueError,
					"bad pickle state");
			PyObjC_GIL_FORWARD_EXC();
		}

		aClass = objc_lookUpClass(PyString_AsString(PyTuple_GET_ITEM(state, 0)));
		if (aClass == nil) {
			PyErr_SetString(PyExc_ValueError,
					"bad pickle state");
			PyObjC_GIL_FORWARD_EXC();
		}
	PyObjC_END_WITH_GIL

	rootObject = [[aClass alloc] initWithCoder:self];
	return self;
}

-(void)dealloc
{
	Py_XDECREF(keyedAttributes);
	Py_XDECREF(attributes);
	[rootObject release];
	[super dealloc];
}


-(NSObject*)rootObject
{
	return rootObject;
}


/* Implementation of the NSCoding protocol starts here */

-(NSInteger)versionForClassName:(NSString*)name
{
	if (strcmp([name UTF8String], className) == 0) {
		return classVersion;
	} else {
		return 0;
	}
}

-(unsigned)systemVersion
{
	return systemVersion;
}

-(BOOL)allowsKeyedCoding
{	
	return YES;
}

-(BOOL)containsValueForKey:(NSString*)key
{
	BOOL result = NO;

	PyObjC_BEGIN_WITH_GIL
		PyObject* pkey = PyObjC_IdToPython(key);
		if (pkey == NULL) {
			PyObjC_GIL_FORWARD_EXC();
		} 

		PyObject* v = PyDict_GetItem(keyedAttributes, pkey);
		if (v == NULL) {
			result = NO;
		} else {
			result = YES;
		}

		Py_DECREF(pkey);

	PyObjC_END_WITH_GIL

	return result;
}

-(BOOL)decodeBoolForKey:(NSString*)key
{
static  char encoding[] = { _C_NSBOOL, 0 };

	BOOL result;

	PyObjC_BEGIN_WITH_GIL

		PyObject* pkey = PyObjC_IdToPython(key);
		PyObject* pval = PyDict_GetItem(keyedAttributes, pkey);

		if (pval == NULL) {
			PyObjC_GIL_RETURN(NO);
		}

		int r = depythonify_c_value(encoding, pval, &result);
		Py_DECREF(pkey);

		if (r == -1) {
			PyObjC_GIL_FORWARD_EXC();
		}
	PyObjC_END_WITH_GIL

	return result;
}

-(uint8_t*)decodeBytesForKey:(NSString*)key returnedLength:(NSUInteger*)length
{
	uint8_t* result;

	PyObjC_BEGIN_WITH_GIL

		PyObject* pkey = PyObjC_IdToPython(key);
		PyObject* pval = PyDict_GetItem(keyedAttributes, pkey);

		if (pval == NULL) {
			*length = 0;
			PyObjC_GIL_RETURN(NULL);
		}

		char* buffer;
		Py_ssize_t sz;

		int r = PyString_AsStringAndSize(pval, &buffer, &sz);

		Py_DECREF(pkey);

		if (r == -1) {
			PyObjC_GIL_FORWARD_EXC();
		}

		*length = sz;
		result = (uint8_t*)buffer;

	PyObjC_END_WITH_GIL

	return result;
}

#define VALUE_KEYED_DECODE(type, dflt) \
	type result;							\
									\
	PyObjC_BEGIN_WITH_GIL						\
									\
		PyObject* pkey = PyObjC_IdToPython(key);		\
		PyObject* pval = PyDict_GetItem(keyedAttributes, pkey);	\
									\
		if (pval == NULL) {					\
			PyObjC_GIL_RETURN(dflt);				\
		}							\
									\
		int r = depythonify_c_value(@encode(type), pval, &result);\
		Py_DECREF(pkey);					\
									\
		if (r == -1) {						\
			PyObjC_GIL_FORWARD_EXC();			\
		}							\
	PyObjC_END_WITH_GIL						\
									\
	return result;

-(double)decodeDoubleForKey:(NSString*)key
{
	VALUE_KEYED_DECODE(double, 0)
}

-(float)decodeFloatForKey:(NSString*)key
{
	VALUE_KEYED_DECODE(double, 0)
}

-(int32_t)decodeInt32ForKey:(NSString*)key
{
	VALUE_KEYED_DECODE(int32_t, 0)	
}

-(int64_t)decodeInt64ForKey:(NSString*)key
{
	VALUE_KEYED_DECODE(int64_t, 0)	
}

-(NSInteger)decodeIntegerForKey:(NSString*)key
{
	VALUE_KEYED_DECODE(NSInteger, 0)	
}

-(int)decodeIntForKey:(NSString*)key
{
	VALUE_KEYED_DECODE(int, 0)	
}

-(id)decodeObjectForKey:(NSString*)key
{
	VALUE_KEYED_DECODE(id, nil)	
}

-(NSPoint)decodePointForKey:(NSString*)key
{
	VALUE_KEYED_DECODE(NSPoint, NSZeroPoint)	
}

-(NSRect)decodeRectForKey:(NSString*)key
{
	VALUE_KEYED_DECODE(NSRect, NSZeroRect)	
}

-(NSSize)decodeSizeForKey:(NSString*)key
{
	VALUE_KEYED_DECODE(NSSize, NSZeroSize)	
}

#define VALUE_DECODE(type) \
	type result;							\
									\
	PyObjC_BEGIN_WITH_GIL						\
									\
		PyObject* pval = PyList_GetItem(attributes, attributeIndex++);	\
									\
		if (pval == NULL) {					\
			PyObjC_GIL_FORWARD_EXC();			\
		}							\
									\
		int r = depythonify_c_value(@encode(type), pval, &result);\
									\
		if (r == -1) {						\
			PyObjC_GIL_FORWARD_EXC();			\
		}							\
	PyObjC_END_WITH_GIL						\
									\
	return result;

-(id)decodeObject
{
	VALUE_DECODE(id)
}

-(void)decodeValueOfObjCType:(const char*)type at:(void*)data
{
									
	PyObjC_BEGIN_WITH_GIL						
									
		PyObject* pval = PyList_GetItem(attributes, attributeIndex++);	
									
		if (pval == NULL) {					
			PyObjC_GIL_FORWARD_EXC();			
		}							
									
		int r = depythonify_c_value(type, pval, data);
									
		if (r == -1) {						
			PyObjC_GIL_FORWARD_EXC();			
		}							
	PyObjC_END_WITH_GIL						
}									

-(uint8_t*)decodeBytesWithReturnedLength:(NSUInteger*)length
{
	uint8_t* result;

	PyObjC_BEGIN_WITH_GIL

		PyObject* pval = PyList_GetItem(attributes, attributeIndex++);	

		if (pval == NULL) {
			PyObjC_GIL_FORWARD_EXC();
		}

		char* buffer;
		Py_ssize_t sz;

		int r = PyString_AsStringAndSize(pval, &buffer, &sz);

		if (r == -1) {
			PyObjC_GIL_FORWARD_EXC();
		}

		*length = sz;
		result = (uint8_t*)buffer;

	PyObjC_END_WITH_GIL

	return result;
}

-(NSData*)decodeData
{
	NSData* result;

	PyObjC_BEGIN_WITH_GIL

		PyObject* pval = PyList_GetItem(attributes, attributeIndex++);	

		if (pval == NULL) {
			PyObjC_GIL_FORWARD_EXC();
		}

		char* buffer;
		Py_ssize_t sz;

		int r = PyString_AsStringAndSize(pval, &buffer, &sz);

		if (r == -1) {
			PyObjC_GIL_FORWARD_EXC();
		}

		result = [NSMutableData dataWithBytes:buffer length:sz];

	PyObjC_END_WITH_GIL

	return result;
}

@end
