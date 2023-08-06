/*
 * Implementation of the NSCoding protocol that uses the Python
 * pickle infrastructure
 *
 * The implementation of __reduce__ for an Objective-C class should
 * create be:
 *
 * 	archiver = [OC_PickleArchiver newWithRootObject:self];
 * 	return [archiver state];
 *
 * The 'objc._recoverPickleArchive' function restores this state.
 *
 * This implementation is not a strict implementation of NSCoding,
 * it is assumed that the initWithCoder:/encodeWithCoder: methods
 * work correctly. One result of this is that is is possible to
 * encode a value as a C type (e.g. encodeInt:forKey:) and then
 * decode it as an Object (decodeObject:forKey:)
 */
#ifndef OC_ReduceArchiver_H
#define OC_ReduceArchiver_H

extern PyObject* PyObjC_recoverArchiveFunc;

@interface OC_PickeArchiver : NSCoder
{
	const char*	className;
	NSInteger	classVersion;
	PyObject* 	keyedAttributes;
	PyObject* 	attributes;
}

+newWithRootObject:(NSObject<NSCoding>*)object;
-initWithRootObject:(NSObject<NSCoding>*)object;

-(PyObject*)state;

@end

@interface OC_PickleUnarchiver : NSCoder
{
	char*		className;
	NSInteger	classVersion;
	unsigned	systemVersion;
	PyObject* 	keyedAttributes;
	PyObject* 	attributes;
	NSObject*	rootObject;
	int		attributeIndex;
}
+newWithState:(PyObject*)state;
-initWithState:(PyObject*)state;
-(NSObject*)rootObject;

@end

#endif /* OC_ReduceArchiver_H */
