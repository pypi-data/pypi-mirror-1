#include "math.h"

#ifndef M_PI
const double M_PI = 3.1415926;
#endif

#ifdef _WIN32
  #define cosf cos
  #define sinf sin
  #define fmodf fmod
  #define expf exp
  #define sqrtf sqrt
#endif
