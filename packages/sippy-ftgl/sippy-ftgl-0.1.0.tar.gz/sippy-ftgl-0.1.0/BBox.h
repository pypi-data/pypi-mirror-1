#ifndef SIPPY_BBOX
#define SIPPY_BBOX

#include <FTGL/FTFont.h>
#include <FTGL/FTGLOutlineFont.h>
#include <FTGL/FTGLPolygonFont.h>
#include <FTGL/FTGLExtrdFont.h>
#include <FTGL/FTGLBitmapFont.h>
#include <FTGL/FTGLTextureFont.h>
#include <FTGL/FTGLPixmapFont.h>



class BBox {

 public:
 BBox() : lowerX(0), lowerY(0), lowerZ(0), upperX(0), upperY(0), upperZ(0) {}
  ~BBox() {}

  void setValuesUsingFont(FTFont* aFont, const char* aString) {
    aFont->BBox(aString, lowerX, lowerY, lowerZ, upperX, upperY, upperZ);
  }

  float lowerX, lowerY, lowerZ, upperX, upperY, upperZ;
};

#endif
