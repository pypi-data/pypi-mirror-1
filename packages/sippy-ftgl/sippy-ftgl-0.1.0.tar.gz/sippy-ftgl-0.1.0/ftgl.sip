%Module FTGL 0


%ModuleHeaderCode
#include <FTGL/ftgl.h>
%End


class FTFont /PyName=Font, Abstract/
{

public:

FTFont( const char* fontFilePath);

bool Attach( const char* fontFilePath) /AutoGen/;
virtual bool FaceSize
	( const unsigned int size, const unsigned int res = 72) /AutoGen/;
virtual void Depth( float depth) /AutoGen/;

void UseDisplayList( bool useList) /AutoGen/;       
float Ascender() const /AutoGen/;
float Descender() const /AutoGen/;
float LineHeight() const /AutoGen/;
float Advance( const char* string) /AutoGen/;
virtual void Render( const char* string) /AutoGen/;

SIP_PYTUPLE BBox(const char*) /AutoGen/;
%MethodCode
	float lowerX, lowerY, lowerZ, upperX, upperY, upperZ;
	sipCpp->FTFont::BBox(a0, lowerX, lowerY, lowerZ, upperX, upperY, upperZ);
	sipRes = sipBuildResult(&sipIsErr, "(ffffff)", lowerX, lowerY, lowerZ, upperX, upperY, upperZ);
%End
};



class FTGLOutlineFont : FTFont /PyName=OutlineFont/
{
public:
FTGLOutlineFont( const char* fontFilePath);
};


class FTGLPolygonFont : FTFont /PyName=PolygonFont/ 
{
public:
FTGLPolygonFont( const char* fontFilePath);
};

class FTGLExtrdFont : FTFont /PyName=ExtrdFont/
{
public:
FTGLExtrdFont( const char* fontFilePath);
};

class FTGLBitmapFont : FTFont /PyName=BitmapFont/ 
{
public:
FTGLBitmapFont( const char* fontFilePath);
};

class FTGLTextureFont : FTFont /PyName=TextureFont/
{
public:
FTGLTextureFont( const char* fontFilePath);
};


class FTGLPixmapFont : FTFont /PyName=PixmapFont/
{
public:
FTGLPixmapFont( const char* fontFilePath);
};



class BBox {

%TypeHeaderCode
#include <BBox.h>
%End

public:
BBox();

void setValuesUsingFont(FTFont* aFont, const char* aString);

float lowerX;
float lowerY; 
float lowerZ;
float upperX;
float upperY;
float upperZ;
};
