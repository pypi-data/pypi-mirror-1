/* Copyright (C) 2008, Charles Wang.
 * Author: Charles Wang <charlesw1234@163.com>
 */
#include  <Python.h>
#include  <sys/time.h>
#include  <stdlib.h>
#include  <gd.h>

typedef PyObject PyObject_t;
typedef PyMethodDef PyMethodDef_t;
typedef gdImagePtr gdImagePtr_t;

static const char * module_name = "_pickey";
static const int default_background[3] = { 255, 255, 255 };
static const int default_monochrome = !0;
static const int default_monofont = 0;
static const int default_minptsize = 60;
static const int default_maxptsize = 100;
static const int default_dot_limit = 32;
static const int default_line_limit = 2;
static const char * default_fontpath = "/usr/share/fonts/corefonts/cour.ttf";

static const char * colors_name[] = { "Red", "Green", "Blue" };

static int
get_random_color(int * background)
{
    int idx, cvalues[3];

    for (idx = 0; idx < 3; ++idx) {
	if (background[idx] < 0x80)
	    cvalues[idx] = 255 - random() % ((255 - background[idx]) / 2);
	else
	    cvalues[idx] = random() % (background[idx] / 2);
    }
    return gdTrueColor(cvalues[0], cvalues[1], cvalues[2]);
}

static const char *
get_random_font(char ** fontpathes, int num_fontpathes)
{
    if (num_fontpathes == 0) return default_fontpath;
    else if (num_fontpathes == 1) return fontpathes[0];
    else return fontpathes[random() % num_fontpathes];
}

static int
min4(int v0, int v1, int v2, int v3)
{
    if (v0 > v1) v0 = v1;
    if (v2 > v3) v2 = v3;
    return v0 < v2 ? v0 : v2;
}
static int
max4(int v0, int v1, int v2, int v3)
{
    if (v0 < v1) v0 = v1;
    if (v2 < v3) v2 = v3;
    return v0 > v2 ? v0 : v2;
}
static int
get_random_pos(int space, int * r)
{
    int min0 = min4(r[0], r[2], r[4], r[6]);
    int space0 = max4(r[0], r[2], r[4], r[6]) - min0;

    if (space > space0 + 1) return random() % (space - space0) - min0;
    if (space > space0 - 1) return -min0;
    return (space - space0) / 2 - min0;
}

typedef struct {
    const char * keystr, * lastkeystr; int lenkeystr;
    int width, height;
    int background[3]; /* Background. */
    int monochrome, monofont;
    int minptsize, maxptsize;
    int dot_limit, line_limit;
    char ** fontpathes;
    int num_fontpathes;
}  authkey_args_t;

static char * kwlist[] = { "key", "width", "height", "background",
			   "monochrome", "monofont",
			   "minptsize", "maxptsize",
			   "dot_limit", "line_limit",
			   "fontpathes", NULL };

static const char * fpseps = " \t\n";

static int
pkargs_setup(authkey_args_t * self, PyObject_t * args, PyObject_t * kwargs)
{
    PyObject_t * background, * monochrome, * monofont, * valobj;
    int idx;
    const char * fontpathes, * curfp;
    char ** curfparr, * curfpstr;

    background = NULL;
    monochrome = NULL;
    monofont = NULL;
    self->minptsize = default_minptsize;
    self->maxptsize = default_maxptsize;
    self->dot_limit = default_dot_limit;
    self->line_limit = default_line_limit;
    fontpathes = "";
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "sii|OOOiiiis", kwlist,
				     &self->keystr,
				     &self->width,
				     &self->height,
				     &background,
				     &monochrome,
				     &monofont,
				     &self->minptsize,
				     &self->maxptsize,
				     &self->dot_limit,
				     &self->line_limit,
				     &fontpathes))
	return -1;

    if ((self->lenkeystr = strlen(self->keystr)) == 0) {
	PyErr_SetString(PyExc_ValueError,
			"key string can not be blank string.");
	return -1;
    }
    self->lastkeystr = self->keystr + self->lenkeystr;

    if (self->width < 32 || self->width > 1000) {
	PyErr_Format(PyExc_ValueError,
		     "Width %d is not in [32, 1000].", self->width);
	return -1;
    }

    if (self->height < 32 || self->height > 1000) {
	PyErr_Format(PyExc_ValueError,
		     "Height %d is not in [32, 1000].", self->height);
	return -1;
    }

    if (!background) {
	self->background[0] = default_background[0];
	self->background[1] = default_background[1];
	self->background[2] = default_background[2];
    } else if (!PyTuple_Check(background)) {
	return -1;
    } else if (PyTuple_Size(background) != 3) {
	PyErr_SetString(PyExc_ValueError, "background should be (r, g, b).");
	return -1;
    } else {
	for (idx = 0; idx < 3; ++idx) {
	    valobj = PyTuple_GET_ITEM(background, idx);
	    if (!PyInt_Check(valobj)) {
		PyErr_Format(PyExc_ValueError,
			     "Color value %s must be integer.",
			     colors_name[idx]);
		return -1;
	    }
	    self->background[idx] = PyInt_AS_LONG(valobj);
	    if (self->background[idx] < 0 ||
		self->background[idx] > 255) {
		PyErr_Format(PyExc_ValueError,
			     "Color %s %d is not in [0, 255].",
			     colors_name[idx], self->background[idx]);
		return -1;
	    }
	}
    }

    if (!monochrome) {
	self->monochrome = default_monochrome;
    } else if (!PyBool_Check(monochrome)) {
	return -1;
    } else {
	self->monochrome = (monochrome == Py_True);
    }

    if (!monofont) {
	self->monofont = default_monofont;
    } else if (!PyBool_Check(monofont)) {
	return -1;
    } else {
	self->monofont = (monofont == Py_True);
    }

    if (self->minptsize < 25 || self->minptsize > 100) {
	PyErr_Format(PyExc_ValueError,
		     "minptsize %d%% is not in [25%, 100%].",
		     self->minptsize);
	return -1;
    }

    if (self->maxptsize < 25 || self->maxptsize > 100) {
	PyErr_Format(PyExc_ValueError,
		     "maxptsize %d%% is not in [25%, 100%].",
		     self->maxptsize);
	return -1;
    }

    if (self->minptsize > self->maxptsize) {
	PyErr_Format(PyExc_ValueError,
		     "Assert(minptsize(%d%%) <= maxptsize(%d%%)) failed.",
		     self->minptsize, self->maxptsize);
	return -1;
    }

    if (self->dot_limit < 0 || self->dot_limit > 255) {
	PyErr_Format(PyExc_ValueError,
		     "Dot limitation %d is not in [0, 255].",
		     self->dot_limit);
	return -1;
    }

    if (self->line_limit < 0 || self->line_limit > 31) {
	PyErr_Format(PyExc_ValueError,
		     "Line limitation %d is not in [0, 31].",
		     self->line_limit);
	return -1;
    }

    /* Count the number of font pathes in fontpathes. */
    self->num_fontpathes = 0; curfp = fontpathes;
    while (*curfp) {
	if (strchr(fpseps, *curfp)) {
	    ++curfp;
	} else {
	    curfp += strcspn(curfp, fpseps);
	    ++self->num_fontpathes;
	}
    }
    if (!(self->fontpathes =
	  malloc(self->num_fontpathes * sizeof(char *) +
		 strlen(fontpathes) + 1))) {
	PyErr_SetString(PyExc_MemoryError, "");
	return -1;
    }

    if (self->num_fontpathes == 0) self->fontpathes = NULL;
    else {
	curfpstr = (char *)(self->fontpathes + self->num_fontpathes);
	curfparr = self->fontpathes;
	memcpy(curfpstr, fontpathes, strlen(fontpathes) + 1);
	while (*curfpstr) {
	    if (strchr(fpseps, *curfpstr)) *curfpstr++ = 0;
	    else {
		*curfparr++ = curfpstr;
		curfpstr += strcspn(curfpstr, fpseps);
	    }
	}
    }

    return 0;
}

static void
add_noise(gdImagePtr_t im, int color, int width, int height,
	  int dot_limit, int line_limit)
{
    int idx, num;

    /* Dot noise */
    num = random() % (dot_limit + 1);
    for (idx = 0; idx < num; ++idx) {
	gdImageSetPixel(im, random() % width, random() % height, color);
    }

    /* Line noise */
    num = random() % (line_limit + 1);
    for (idx = 0; idx < num; ++idx) {
	gdImageLine(im, random() % width, random() % height,
		    random() % width, random() % height, color);
    }
}

static gdImagePtr_t
pkargs_render(authkey_args_t * self)
{
    gdImagePtr_t im;
    char str[2];
    double x, xspace, y, yspace;
    double ptsize, ptsize100;
    const char * cur;
    int color; double angle;
    const char * font;
    int brect[8];
    char * err;

    if (!(im = gdImageCreateTrueColor(self->width, self->height))) {
	PyErr_SetString(PyExc_RuntimeError,
			"gdImageCreateTrueColor failed.");
	goto errquit0;
    }
    gdImageFilledRectangle(im, 0, 0, self->width, self->height,
			   gdTrueColor(self->background[0],
				       self->background[1],
				       self->background[2]));

    str[1] = 0;
    x = 4; xspace = (self->width - 8) / self->lenkeystr;
    y = self->height / 8; yspace = (double)self->height * 3 / 4;
    ptsize100 = yspace;
    if (self->monochrome) color = get_random_color(self->background);
    if (self->monofont)
	font = get_random_font(self->fontpathes, self->num_fontpathes);
    if (self->minptsize == self->maxptsize)
	ptsize = ptsize100 * self->minptsize / 100;
    for (cur = self->keystr; cur < self->lastkeystr; ++cur) {
	str[0] = *cur;
	if (!self->monochrome) color = get_random_color(self->background);
	if (!self->monofont)
	    font = get_random_font(self->fontpathes, self->num_fontpathes);
	if (self->minptsize < self->maxptsize)
	    ptsize = ptsize100 * (self->minptsize +
				  random() % (self->maxptsize -
					      self->minptsize + 1)) / 100;
	angle = (double)(random() & 0xFF) * 1.6 / 256 - 0.8;

	add_noise(im, color, self->width, self->height,
		  self->dot_limit, self->line_limit);
	if ((err = gdImageStringFT(NULL, &brect[0], color, (char *)font,
				   ptsize, angle, 0, 0, str))) {
	    PyErr_Format(PyExc_RuntimeError,
			 "gdImageStringFT failed: %s", str);
	    goto errquit1;
	}
	if ((err = gdImageStringFT(im, &brect[0], color, (char *)font,
				   ptsize, angle,
				   x + get_random_pos(xspace, brect),
				   y + get_random_pos(yspace, brect + 1),
				   str))) {
	    PyErr_Format(PyExc_RuntimeError,
			 "gdImageStringFT failed: %s", str);
	    goto errquit1;
	}
	x += xspace;
    }
    return im;
 errquit1:
    gdImageDestroy(im);
 errquit0:
    return NULL;
}

static void
pkargs_finish(authkey_args_t * self)
{
    if (self->fontpathes) free(self->fontpathes);
}

static PyObject_t *
PicKey_GetPNG(PyObject_t * self, PyObject_t * args, PyObject_t * kwargs)
{
    authkey_args_t pkargs;
    gdImagePtr im;
    void * png; int szpng;
    PyObject_t * result;

    if (pkargs_setup(&pkargs, args, kwargs) < 0) goto errquit0;

    if (!(im = pkargs_render(&pkargs))) goto errquit1;

    if (!(png = gdImagePngPtr(im, &szpng))) {
	PyErr_SetString(PyExc_RuntimeError, "gdImagePngPtr failed.");
	goto errquit2;
    }

    if (!(result = PyString_FromStringAndSize(png, szpng)))
	goto errquit3;

    gdFree(png);
    gdImageDestroy(im);
    pkargs_finish(&pkargs);
    return result;
 errquit3:
    gdFree(png);
 errquit2:
    gdImageDestroy(im);
 errquit1:
    pkargs_finish(&pkargs);
 errquit0:
    return NULL;
}

static PyMethodDef_t PicKey_Methods[] = {
    { "GetPNG", (PyCFunction)PicKey_GetPNG,
      METH_VARARGS | METH_KEYWORDS, NULL },
    { NULL, NULL }
};

PyMODINIT_FUNC
init_pickey(void)
{
    struct timeval tv;
    PyObject_t * module;

    gettimeofday(&tv, NULL);
    srandom((unsigned int)tv.tv_usec);

    module = Py_InitModule(module_name, PicKey_Methods);
}
