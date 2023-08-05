
/* PIL module for the PXC-200 frame grabber driver */
/* Written by A.M. Kuchling */

/* $Id: pxc200module.c 21202 2003-03-18 18:42:46Z akuchlin $ */

#include "Python.h"
#include "Imaging/Imaging.h"
#include "pxc200.h"
#include <sys/mman.h>

static PyObject *
PyPXC200_snap(self, args)
	PyObject *self;
	PyObject *args;
{
  long L;
  int fd, size, x,y, nbytes, total_bytes;
  Imaging im;
  unsigned char *mapped_area, *p;
  
  if (!PyArg_ParseTuple(args, "ii", &fd, &L))
    return NULL;
  im = (Imaging) L;

  /* The image data will be read in chunks of BUFSIZE pixels at a time. */
#define BUFSIZE 2048

  /* Read from the file descriptor */
  total_bytes = im->xsize * im->ysize * 3;
  x=0; y=0; 
  while (y < im->ysize) {
    unsigned char buffer[3 * BUFSIZE];
    unsigned char *pix = buffer;
    int to_read = total_bytes;
    
    if (to_read > sizeof(buffer)) 
      to_read = sizeof(buffer);

    Py_BEGIN_ALLOW_THREADS;
    nbytes = read(fd, buffer, to_read );
    Py_END_ALLOW_THREADS;
    total_bytes -= nbytes;

    if (nbytes == -1 ) { 
      PyErr_SetFromErrno(PyExc_IOError);     
      return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    while (nbytes>0 && y < im->ysize) {
      im->image32[y][x] = (  pix[0] <<16 ) + (pix[1]<<8) + pix[2];
      /* printf("%i %i %06x\n", x,y,im->image32[y][x]);*/
      pix += 3; nbytes -= 3;

      /* Increment to the next pixel */
      if (++x >= im->xsize)
	{x = 0; y++;}
    }
    Py_END_ALLOW_THREADS
  } /* end while (y < im->ysize) */

#if 0
  /* The mmap support in the PXC-0.21 driver seems to be broken, so 
     this code doesn't work. */

  size = im->xsize * im->ysize;
  mapped_area = mmap(NULL, size, PROT_READ, MAP_SHARED, 
		     fd, 0);

  if (mapped_area == NULL) {
    PyErr_SetString(PyExc_IOError, "Unable to mmap file descriptor");
    return NULL;
  }t.

  x=0; y=0; p=mapped_area;
  while (y < im->ysize) {
    im->image32[y][x] = ( (*p)<<16 ) + (*(p+1)<<8) + *(p+2);
    /*printf("%i %i %06x\n", x,y,im->image32[y][x]);*/

    /* Increment to the next pixel */
    if (++x >= im->xsize)
      {x = 0; y++;}
  }

  munmap(mapped_area, size);
#endif

  Py_INCREF(Py_None);
  return Py_None;
}

/* List of functions defined in the module */

static PyMethodDef PyPXC200_methods[] = {
	{"snap",	PyPXC200_snap,		1},
	{NULL,		NULL}		/* sentinel */
};

static void
insint(d, name, value)
     PyObject *d;
     char *name;
     int value;
{
	PyObject *v = PyInt_FromLong((long) value);
	if (!v || PyDict_SetItemString(d, name, v))
		Py_FatalError("can't initialize sane module");

	Py_DECREF(v);
}


void
initpxc200()
{
	PyObject *m, *d;

	/* Create the module and add the functions */
	m = Py_InitModule("pxc200", PyPXC200_methods);

	/* Add symbolic constants for the ioctls */
	d = PyModule_GetDict(m);

	insint(d, "PX_IOCRESET", PX_IOCRESET);
	insint(d, "PX_IOCHARDRESET", PX_IOCHARDRESET);
	insint(d, "PX_IOCGFLAGS", PX_IOCGFLAGS);
	insint(d, "PX_IOCSFLAGS", PX_IOCSFLAGS);
	insint(d, "PX_IOCGDMASIZE", PX_IOCGDMASIZE);
	insint(d, "PX_IOCGDMABUF", PX_IOCGDMABUF);
	insint(d, "PX_IOCGRISCADDE", PX_IOCGRISCADDE);
	insint(d, "PX_IOCGRISCADDO", PX_IOCGRISCADDO);
	insint(d, "PX_IOCGPROGRAME", PX_IOCGPROGRAME);
	insint(d, "PX_IOCGPROGRAMO", PX_IOCGPROGRAMO);
	insint(d, "PX_IOCGIRQCOUNT", PX_IOCGIRQCOUNT);
	insint(d, "PX_IOCGREFV", PX_IOCGREFV);
	insint(d, "PX_IOCSREFV", PX_IOCSREFV);
	insint(d, "PX_IOCSMUX", PX_IOCSMUX);
	insint(d, "PX_IOCGMUX", PX_IOCGMUX);
	insint(d, "PX_IOCSTRIG", PX_IOCSTRIG);
	insint(d, "PX_IOCSACQLEN", PX_IOCSACQLEN);
	insint(d, "PX_IOCGACQLEN", PX_IOCGACQLEN);
	insint(d, "PX_IOCACQNOW", PX_IOCACQNOW);
	insint(d, "PX_IOCWAITVB", PX_IOCWAITVB);
	insint(d, "PX_IOCSEQUENCE", PX_IOCSEQUENCE);
	insint(d, "PX_IOCGHWOVERRUN", PX_IOCGHWOVERRUN);
	insint(d, "PX_IOCGSWOVERRUN", PX_IOCGSWOVERRUN);
#ifdef PX_IOCGWHOLEDEVICE
	insint(d, "PX_IOCGWHOLEDEVICE", PX_IOCGWHOLEDEVICE);
#endif
	insint(d, "PX_IOCGBRIGHT", PX_IOCGBRIGHT);
	insint(d, "PX_IOCSBRIGHT", PX_IOCSBRIGHT);
	insint(d, "PX_IOCGCONTRAST", PX_IOCGCONTRAST);
	insint(d, "PX_IOCSCONTRAST", PX_IOCSCONTRAST);
	insint(d, "PX_IOCGHUE", PX_IOCGHUE);
	insint(d, "PX_IOCSHUE", PX_IOCSHUE);
	insint(d, "PX_IOCGSATU", PX_IOCGSATU);
	insint(d, "PX_IOCSSATU", PX_IOCSSATU);
	insint(d, "PX_IOCGSATV", PX_IOCGSATV);
	insint(d, "PX_IOCSSATV", PX_IOCSSATV);
#ifdef PX_IOCINFOBUF
	insint(d, "PX_IOCINFOBUF", PX_IOCINFOBUF);
#endif
#ifdef PX_IOCDONEBUF
	insint(d, "PX_IOCDONEBUF", PX_IOCDONEBUF);
#endif

	if (PyErr_Occurred())
		Py_FatalError("can't initialize module pxc200");


}
