"""
Copyright (C) 1999-2002 Adam D. Moss (the "Author").  All Rights Reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is fur-
nished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FIT-
NESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CON-
NECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Except as contained in this notice, the name of the Author of the
Software shall not be used in advertising or otherwise to promote the sale,
use or other dealings in this Software without prior written authorization
from the Author.

Ported to Python by David Gowers, 2007 <3

"""

tmp = """
  cpercep.c: The CPercep Functions v0.9: 2002-02-10
  Adam D. Moss: adam@gimp.org <http://www.foxbox.org/adam/code/cpercep/>

  This code module concerns itself with conversion from a hard-coded
  RGB colour space (sRGB by default) to CIE L*a*b* and back again with
  (primarily) precision and (secondarily) speed, oriented largely
  towards the purposes of quantifying the PERCEPTUAL difference between
  two arbitrary RGB colours with a minimum of fuss.

  Motivation One: The author is disheartened at the amount of graphics
  processing software around which uses weighted or non-weighted
  Euclidean distance between co-ordinates within a (poorly-defined) RGB
  space as the basis of what should really be an estimate of perceptual
  difference to the human eye.  Certainly it's fast to do it that way,
  but please think carefully about whether your particular application
  should be tolerating sloppy results for the sake of real-time response.

  Motivation Two: Lack of tested, re-usable and free code available
  for this purpose.  The difficulty in finding something similar to
  CPercep with a free license motivated this project; I hope that this
  code also serves to illustrate how to perform the
  R'G'B'->XYZ->L*a*b*->XYZ->R'G'B' transformation correctly since I
  was distressed to note how many of the equations and code snippets
  on the net were omitting the reverse transform and/or were using
  incorrectly-derived or just plain wrong constants.

  TODO: document functions, rename erroneously-named arguments
"""

def cbrt(v):
    return pow(v, 1.0/3.0)


# defines:
#
#  SANITY: emits warnings when passed non-sane colours (and usually
#   corrects them) -- useful when debugging.

#   APPROX: speeds up the conversion from RGB to the colourspace by
#   assuming that the RGB values passed in are integral and definitely
#   in the range 0->255
#
#   SRGB: assumes that the RGB values being passed in (and out) are
#   destined for an sRGB-alike display device (a typical modern monitor)
#   -- if you change this then you'll probably want to change ASSUMED_GAMMA,
#   the phosphor colours and the white point definition.
# */

# /* #define SANITY */
APPROX = True
SRGB = True

if SRGB:
    ASSUMED_GAMMA = 2.2
else:
    ASSUMED_GAMMA = 2.2

REV_GAMMA = ((1.0 / ASSUMED_GAMMA))

#/* define characteristics of the source RGB space (and the space
#   within which we try to behave linearly). */

#/* Phosphor colours: */

#/* sRGB/HDTV phosphor colours */
pxr = 0.64;
pyr = 0.33;
pxg = 0.30;
pyg = 0.60;
pxb = 0.15;
pyb = 0.06;

#/* White point: */

#/* D65 (6500K) (recommended but not a common display default) */
lxn = 0.312713;
lyn = 0.329016;

#/* D50 (5000K) */
#/*static const double lxn = 0.3457F; */
#/*static const double lyn = 0.3585F; */

#/* D55 (5500K) */
#/*static const double lxn = 0.3324F; */
#/*static const double lyn = 0.3474F; */

#/* D93 (9300K) (a common monitor default, but poor colour reproduction) */
#/* static const double lxn = 0.2848F; */
#/* static const double lyn = 0.2932F; */

#/* illum E (normalized) */
#/*static const double lxn = 1.0/3.0F; */
#/*static const double lyn = 1.0/3.0F; */

#/* illum C (average sunlight) */
#/*static const double lxn = 0.3101F; */
#/*static const double lyn = 0.3162F; */

#/* illum B (direct sunlight) */
#/*static const double lxn = 0.3484F; */
#/*static const double lyn = 0.3516F; */

#/* illum A (tungsten lamp) */
#/*static const double lxn = 0.4476F; */
#/*static const double lyn = 0.4074F; */

# ???

LRAMP = 7.99959199;


# init them.. for what?
xnn = 0.0
znn = 0.0

powtable = [0.0] * 256;

def CLAMP (x,l,u):
    return min( u,max(l,x))

def init_powtable(gamma):
    i = 0

    if not SRGB:
    #  /* pure gamma function */
	for i in range(256):
    	    powtable[i] = pow((i)/255.0, gamma);
    else:
    #  /* sRGB gamma curve */
	for i in range(11):
	    powtable[i] = (i) / (255.0 * 12.92);
	for i in range(11,256):
    	    powtable[i] = pow( (((i) / 255.0) + 0.055) / 1.055, 2.4);


#typedef double CMatrix[3][3];
#typedef double CVector[3];

def CMatrix():
    l = list()
    for i in range(3):
        l2 = list()
        l2.append(0.0)
        l2.append(0.0)
        l2.append(0.0)
        l.append(l2)
        
    return l

def CVector():
    """ Is not used. (?)"""
    return [0,0,0]

Mrgb_to_xyz = CMatrix()
Mxyz_to_rgb = CMatrix()

def Minvert (src, dest):
    dest[0][0] = src[1][1] * src[2][2] - src[1][2] * src[2][1];
    dest[0][1] = src[0][2] * src[2][1] - src[0][1] * src[2][2];
    dest[0][2] = src[0][1] * src[1][2] - src[0][2] * src[1][1];
    dest[1][0] = src[1][2] * src[2][0] - src[1][0] * src[2][2];
    dest[1][1] = src[0][0] * src[2][2] - src[0][2] * src[2][0];
    dest[1][2] = src[0][2] * src[1][0] - src[0][0] * src[1][2];
    dest[2][0] = src[1][0] * src[2][1] - src[1][1] * src[2][0];
    dest[2][1] = src[0][1] * src[2][0] - src[0][0] * src[2][1];
    dest[2][2] = src[0][0] * src[1][1] - src[0][1] * src[1][0];

    det = src[0][0] * dest[0][0] + src[0][1] * dest[1][0] + src[0][2] * dest[2][0];

    if (det <= 0.0):
	#print "OutOfRange det: %f" % det
	return 0

    dest[0][0] /= det;
    dest[0][1] /= det;
    dest[0][2] /= det;
    dest[1][0] /= det;
    dest[1][1] /= det;
    dest[1][2] /= det;
    dest[2][0] /= det;
    dest[2][1] /= det;
    dest[2][2] /= det;

    return 1


def rgbxyzrgb_init():
    global xnn,znn
    init_powtable (ASSUMED_GAMMA);

    xnn = lxn / lyn
#  /* ynn taken as 1.0 */
    znn = (1.0 - (lxn + lyn)) / lyn
#    print "INIT .. Xnn, Znn = %r %r" % (xnn,znn)

    MRC = CMatrix()
    MRCi = CMatrix()

    MRC[0][0] = pxr;
    MRC[0][1] = pxg;
    MRC[0][2] = pxb;
    MRC[1][0] = pyr;
    MRC[1][1] = pyg;
    MRC[1][2] = pyb;
    MRC[2][0] = 1.0 - (pxr + pyr);
    MRC[2][1] = 1.0 - (pxg + pyg);
    MRC[2][2] = 1.0 - (pxb + pyb);

    Minvert (MRC, MRCi);

    C1 = MRCi[0][0]*xnn + MRCi[0][1] + MRCi[0][2]*znn;
    C2 = MRCi[1][0]*xnn + MRCi[1][1] + MRCi[1][2]*znn;
    C3 = MRCi[2][0]*xnn + MRCi[2][1] + MRCi[2][2]*znn;

    Mrgb_to_xyz[0][0] = MRC[0][0] * C1;
    Mrgb_to_xyz[0][1] = MRC[0][1] * C2;
    Mrgb_to_xyz[0][2] = MRC[0][2] * C3;
    Mrgb_to_xyz[1][0] = MRC[1][0] * C1;
    Mrgb_to_xyz[1][1] = MRC[1][1] * C2;
    Mrgb_to_xyz[1][2] = MRC[1][2] * C3;
    Mrgb_to_xyz[2][0] = MRC[2][0] * C1;
    Mrgb_to_xyz[2][1] = MRC[2][1] * C2;
    Mrgb_to_xyz[2][2] = MRC[2][2] * C3;

    Minvert (Mrgb_to_xyz, Mxyz_to_rgb);



def xyz_to_rgb (x,y,z):
    """ NOTE: semantic change:
    
        xyz_to_rgb(x,y,z) -> xyz now hold RGB values
	becomes
	r,g,b = xyz_to_rgb(x,y,z)
    """
    r = Mxyz_to_rgb[0][0]*x + Mxyz_to_rgb[0][1]*y + Mxyz_to_rgb[0][2]*z
    g = Mxyz_to_rgb[1][0]*x + Mxyz_to_rgb[1][1]*y + Mxyz_to_rgb[1][2]*z
    b = Mxyz_to_rgb[2][0]*x + Mxyz_to_rgb[2][1]*y + Mxyz_to_rgb[2][2]*z
    return r,g,b



def rgb_to_xyz (r,g,b):
    """ See above -- matching semantic change"""
#    print "RGB2XYZ IN ",r,g,b
    x = Mrgb_to_xyz[0][0]*r + Mrgb_to_xyz[0][1]*g + Mrgb_to_xyz[0][2]*b;
    y = Mrgb_to_xyz[1][0]*r + Mrgb_to_xyz[1][1]*g + Mrgb_to_xyz[1][2]*b;
    z = Mrgb_to_xyz[2][0]*r + Mrgb_to_xyz[2][1]*g + Mrgb_to_xyz[2][2]*b;
    return x, y, z



def ffunc(t):
  if (t > 0.008856):
      return (cbrt(t))
  else:
      return (7.787 * t + 16.0/116.0)


def ffunc_inv(t):
  if (t > 0.206893):
      return (t * t * t)
  else:
      return ((t - 16.0/116.0) / 7.787)



def xyz_to_lab (X,Y,Z):
#    print 'XYZ', X,Y,Z
    if (Y > 0.0):
        if (Y > 0.008856):
            L = (116.0 * cbrt(Y)) - 16.0;
        else:
            L = (Y * 903.3);

##ifdef SANITY
#      if (L < 0.0F)
#        {
#          g_printerr (" <eek1>%f \007",(float)L);
#        }
#
#      if (L > 100.0F)
#        {
#          g_printerr (" <eek2>%f \007",(float)L);
#        }
##endif
    else:
        L = 0.0;

    ffuncY = ffunc (Y);
#    print '500 * (ffunc(%r/%r) - %r)' % (X,xnn,ffuncY)
    a = 500.0 * (ffunc(X/xnn) - ffuncY);
    b = 200.0 * (ffuncY - ffunc(Z/znn));

    return L,a,b


def lab_to_xyz (L,a,b):
    if (L > LRAMP):
        P = Y = (L + 16.0) / 116.0;
        Y = Y * Y * Y;
    else:
        Y = L / 903.3;
        P = 7.787 * Y + 16.0/116.0;

    X = (P + a / 500.0);
    X = xnn * ffunc_inv(X);
    Z = (P - b / 200.0);
    Z = znn * ffunc_inv(Z);

##ifdef SANITY
#  if (X<-0.00000F)
#    {
#      if (X<-0.0001F)
#        g_printerr ("{badX %f {%f,%f,%f}}",X,L,a,b);
#      X = 0.0F;
#    }
#  if (Y<-0.00000F)
#    {
#      if (Y<-0.0001F)
#        g_printerr ("{badY %f}",Y);
#      Y = 0.0F;
#    }
#  if (Z<-0.00000F)
#    {
#      if (Z<-0.1F)
#        g_printerr ("{badZ %f}",Z);
#      Z = 0.0F;
#    }
#endif
    return X,Y,Z

#/* call this before using the CPercep function */

_inited = False

def cpercep_init ():
    global _inited
    if not _inited:
        rgbxyzrgb_init();
        _inited = True


def rgb_to_lab (r,g,b):
#                      double *outr,
#                      double *outg,
#                      double *outb)
    if APPROX:
#        print r,g,b
##ifdef SANITY
#  /* ADM extra sanity */
#  if ((inr) > 255.0F ||
#      (ing) > 255.0F ||
#      (inb) > 255.0F ||
#      (inr) < -0.0F ||
#      (ing) < -0.0F ||
#      (inb) < -0.0F
#      )
#    abort();
##endif /* SANITY */
	r = powtable[int (r)];
	g = powtable[int (g)];
	b = powtable[int (b)];
    else:
	if SRGB:
#ifdef SRGB
#  /* sRGB gamma curve */
	    r,g,b = [v / (255.0 * 12.92) if v <= (0.03928 * 255.0) else pow( (v + (0.055 * 255.0)) / (1.055 * 255.0), 2.4) for v in (r,g,b)]
	else:
#  /* pure gamma function */
	    r = pow((r)/255.0, ASSUMED_GAMMA);
	    g = pow((g)/255.0, ASSUMED_GAMMA);
	    b = pow((b)/255.0, ASSUMED_GAMMA);
#endif /* SRGB */
#endif /* APPROX */

#ifdef SANITY
#  /* ADM extra sanity */
#  if ((inr) > 1.0F ||
#      (ing) > 1.0F ||
#      (inb) > 1.0F ||
#      (inr) < 0.0F ||
#      (ing) < 0.0F ||
#      (inb) < 0.0F
#      )
#    {
#      g_printerr ("%%");
#      /* abort(); */
#    }
#endif /* SANITY */

    x,y,z = rgb_to_xyz(r, g, b);

#ifdef SANITY
#  if (inr < 0.0F || ing < 0.0F || inb < 0.0F)
#    {
#      g_printerr (" [BAD2 XYZ: %f,%f,%f]\007 ",
#              inr,ing,inb);
#    }
#endif /* SANITY */

    L,A,B = xyz_to_lab(x,y,z);
    return L, A, B


def lab_to_rgb (L,A,B):
    x,y,z = lab_to_xyz(L,A,B);
#    print "L2R xyz", x,y,z
    r,g,b = xyz_to_rgb(x,y,z);
#    print "RGB",r,g,b

#    /* yes, essential.  :( */
    r,g,b = [CLAMP(v,0.0,1.0) for v in (r,g,b)]

    if SRGB:
	r,g,b = [v * (12.92 * 255.0) if v <= 0.0030402477 else pow(v, 1.0/2.4) * (1.055 * 255.0) - (0.055 * 255.0) for v in (r,g,b)]
    else:
#ifdef SRGB
    	r = pow((r)/255.0, ASSUMED_GAMMA);
	g = pow((g)/255.0, ASSUMED_GAMMA);
	b = pow((b)/255.0, ASSUMED_GAMMA);

    return r,g,b


cpercep_init()

EXPERIMENTAL = """
#if 0
/* EXPERIMENTAL SECTION */

const double
xscaler(const double start, const double end,
        const double me, const double him)
{
  return start + ((end-start) * him) / (me + him);
}


void
mix_colours (const double L1, const double a1, const double b1,
             const double L2, const double a2, const double b2,
             double *rtnL, double *rtna, double *rtnb,
             double mass1, double mass2)
{
  double w1, w2;

#if 0
  *rtnL = xscaler (L1, L2, mass1, mass2);
  *rtna = xscaler (a1, a2, mass1, mass2);
  *rtnb = xscaler (b1, b2, mass1, mass2);
#else

#if 1
  w1 = mass1 * L1;
  w2 = mass2 * L2;
#else
  w1 = mass1 * (L1*L1*L1);
  w2 = mass2 * (L2*L2*L2);
#endif

  *rtnL = xscaler (L1, L2, mass1, mass2);

  if (w1 <= 0.0 &&
      w2 <= 0.0)
    {
      *rtna =
        *rtnb = 0.0;
#ifdef SANITY
      /* g_printerr ("\007OUCH. "); */
#endif
    }
  else
    {
      *rtna = xscaler(a1, a2, w1, w2);
      *rtnb = xscaler(b1, b2, w1, w2);
    }
#endif
}
#endif /* EXPERIMENTAL SECTION */
"""

# obsolete LAB object was here -- see palette.py for non-obsolete

            
