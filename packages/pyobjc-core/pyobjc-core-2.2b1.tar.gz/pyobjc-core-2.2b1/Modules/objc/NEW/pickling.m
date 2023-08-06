#include "Python.h"
#include "pyobjc-api.h"

#import <Foundation/Foundation.h>

@interface OC_Codable : NSObject <NSCoding>
{ 
	float	floatValue;
	double	doubleValue;
	int	intValue;
	int64_t	int64Value;
	id	idValue;
}
@end

@implementation OC_Codable

-(void)setFloatValue:(float)value
{
	floatValue = value;
}

-(void)setDoubleValue:(double)value
{
	doubleValue = value;
}

-(void)setIntValue:(int)value
{
	intValue = value;
}

-(void)setInt64Value:(int64_t)value
{
	int64Value = value;
}

-(void)setIdValue:(id)value
{
	idValue = value;
}

-(id)idValue 
{
	return idValue;
}

-(float)floatValue
{
	return floatValue;
}

-(int)intValue
{
	return intValue;
}

-(int64_t)int64Value
{
	return int64Value;
}

-(double)doubleValue
{
	return doubleValue;
}


-(void)encodeWithCoder:(NSCoder*)coder
{
	[coder encodeDouble:doubleValue forKey:@"doubleValue"];
	[coder encodeFloat:floatValue forKey:@"floatValue"];
	[coder encodeInt:intValue forKey:@"intValue"];
	[coder encodeInt64:int64Value forKey:@"int64Value"];
	if (idValue) {
		[coder encodeObject:idValue forKey:@"idValue"];
	}
}

-(id)init
{
	[super init];
	floatValue = 0;
	intValue = 0;
	int64Value = 0;
	idValue = nil;
	return self;
}

-(id)initWithCoder:(NSCoder*)coder
{
	[super init];
	int64Value = [coder decodeInt64ForKey:@"int64Value"];
	intValue = [coder decodeIntForKey:@"intValue"];
	floatValue = [coder decodeFloatForKey:@"floatValue"];
	doubleValue = [coder decodeDoubleForKey:@"doubleValue"];
	idValue = [[coder decodeObjectForKey:@"idValue"] retain];

	return self;
}

@end


static PyMethodDef mod_methods[] = {
	{ 0, 0, 0, 0 }
};

void initpickling(void);
void initpickling(void)
{
	PyObject* m;

	m = Py_InitModule4("pickling", mod_methods, 
			NULL, NULL, PYTHON_API_VERSION);

	PyObjC_ImportAPI(m);
	PyModule_AddObject(m, "OC_Codable",
		PyObjCClass_New([OC_Codable class]));
}
