// oggvideopreview - Python extension to get preview images from
// Theora videos in Ogg files
//
// 2009 Fredrik Portstrom
//
// I, the copyright holder of this file, hereby release it into the
// public domain. This applies worldwide. In case this is not legally
// possible: I grant anyone the right to use this work for any
// purpose, without any conditions, unless such conditions are
// required by law.

#define BUFFER_LENGTH 65536
#define STREAM_COUNT_MAX 4

#include <ogg/ogg.h>
#include <Python.h>
#include <theora/theoradec.h>

static PyObject *convert_frame(th_info *info, th_dec_ctx *decode)
{
  th_ycbcr_buffer buffer;
  th_decode_ycbcr_out(decode, buffer);
  int length = 3 * info->pic_width * info->pic_height;
  PyObject *image_data = PyString_FromStringAndSize(NULL, length);

  if(!image_data)
    {
      return NULL;
    }

  int offset_x = info->pic_x / 2;
  int offset_y = info->pic_y / 2;
  int rgb_padding = 3 * info->pic_width;
  int y_padding = 2 * buffer[0].stride - buffer[0].width;
  int cb_padding = buffer[1].stride - buffer[1].width;
  int cr_padding = buffer[2].stride - buffer[2].width;
  unsigned char *rgb1 = (unsigned char *)PyString_AS_STRING(image_data); // odd row
  unsigned char *rgb2 = rgb1 + rgb_padding; // even row
  unsigned char *rgb_max = rgb1 + rgb_padding * info->pic_height;
  unsigned char *y1 = buffer[0].data + 2 * buffer[0].stride * offset_y + 2 * offset_x; // odd row
  unsigned char *y2 = y1 + buffer[0].stride; // even row
  unsigned char *cb = buffer[1].data + buffer[1].stride * offset_y + offset_x;
  unsigned char *cr = buffer[2].data + buffer[2].stride * offset_y + offset_x;

#define CLAMP (c <= 0 ? 0 : c >= 65025 ? 255 : c >> 8)
#define PIXEL(y_pointer, rgb_pointer) {		\
    int y = 298 * (*y_pointer - 16);		\
    int c = y + r;				\
    *rgb_pointer = CLAMP;			\
    c = y - br;					\
    rgb_pointer[1] = CLAMP;			\
    c = y + b;					\
    rgb_pointer[2] = CLAMP;			\
    y_pointer++;				\
    rgb_pointer += 3;				\
  }

  while(rgb1 < rgb_max)
    {
      unsigned char *y1_max = y1 + buffer[0].width;

      while(y1 < y1_max)
	{
	  int b = *cb - 128;
	  int r = *cr - 128;
	  int br = 100 * b + 208 * r;
	  b *= 516;
	  r *= 409;
	  PIXEL(y1, rgb1);
	  PIXEL(y1, rgb1);
	  PIXEL(y2, rgb2);
	  PIXEL(y2, rgb2);
	  cb++;
	  cr++;
	}

      rgb1 += rgb_padding;
      rgb2 += rgb_padding;
      y1 += y_padding;
      y2 += y_padding;
      cb += cb_padding;
      cr += cr_padding;
    }

  PyObject *tuple = Py_BuildValue("iiiiO", info->pic_width, info->pic_height,
      info->aspect_numerator, info->aspect_denominator, image_data);
  Py_DECREF(image_data);
  return tuple;
}

static PyObject *oggvideopreview_make_preview(PyObject *self, PyObject *args)
{
  char *path;

  if(!PyArg_ParseTuple(args, "s", &path))
    {
      return NULL;
    }

  FILE *file;
  Py_BEGIN_ALLOW_THREADS;
  file = fopen(path, "rb");
  Py_END_ALLOW_THREADS;

  if(!file)
    {
      PyErr_SetFromErrnoWithFilename(PyExc_IOError, path);
      return NULL;
    }

  ogg_sync_state sync;
  ogg_sync_init(&sync);
  int stream_count = 0;
  int killed_streams[STREAM_COUNT_MAX];
  ogg_stream_state streams[STREAM_COUNT_MAX];
  int serial = 0; // Initialize to keep compiler from complaining
  int stream_index = 0; // Initialize to keep compiler from complaining
  int found_theora_stream = 0;
  th_info info;
  th_info_init(&info);
  th_comment comment;
  th_comment_init(&comment);
  th_setup_info *setup = NULL;
  th_dec_ctx *decode = NULL;
  PyObject *result = NULL;

  // Loop 1: Read data from Ogg file

  for(;;)
    {
      char *buffer = ogg_sync_buffer(&sync, BUFFER_LENGTH);

      if(!buffer)
	{
	  PyErr_NoMemory();
	  goto clean_up;
	}

      int length;
      Py_BEGIN_ALLOW_THREADS;
      length = fread(buffer, 1, BUFFER_LENGTH, file);
      Py_END_ALLOW_THREADS;

      if(!length)
	{
	  PyErr_SetFromErrnoWithFilename(PyExc_IOError, path);
	  goto clean_up;
	}

      ogg_sync_wrote(&sync, length);

      // Loop 2: Get Ogg pages and pass to streams

      for(;;)
	{
	  ogg_page page;
	  int ogg_result = ogg_sync_pageseek(&sync, &page);

	  if(!ogg_result)
	    {
	      break;
	    }

	  if(ogg_result < 0)
	    {
	      PyErr_SetString(PyExc_IOError, "Not a valid Ogg file");
	      goto clean_up;
	    }

	  if(!found_theora_stream)
	    {
	      serial = ogg_page_serialno(&page);
	      stream_index = stream_count;

	      // Set stream_index to the index of the stream with matching
	      // serial number in streams if any, otherwise -1.
	      for(;;)
		{
		  stream_index--;

		  if(stream_index < 0 || streams[stream_index].serialno == serial)
		    {
		      break;
		    }
		}

	      if(ogg_page_bos(&page))
		{
		  if(stream_index >= 0)
		    {
		      PyErr_SetString(PyExc_IOError, "Ogg file contains two BOS pages for the same stream");
		      goto clean_up;
		    }

		  // Silently ignore new streams after discovering
		  // STREAM_COUNT_MAX streams.
		  if(stream_count < STREAM_COUNT_MAX - 1)
		    {
		      stream_index = stream_count;
		      stream_count++;
		      killed_streams[stream_index] = 0;
		      ogg_stream_init(streams + stream_index, serial);
		    }
		}

	      // Silently drop pages for unknown and killed streams.
	      if(stream_index < 0 || killed_streams[stream_index])
		{
		  continue;
		}
	    }
	  else if(ogg_page_serialno(&page) != serial)
	    {
	      continue;
	    }

	  // Silently ignore errors.
	  ogg_stream_pagein(streams + stream_index, &page);

	  // Loop 3: Take packets from stream and pass to Theora decoder

	  for(;;)
	    {
	      ogg_packet packet;

	      if(!ogg_stream_packetout(streams + stream_index, &packet))
		{
		  break;
		}

	      int theora_result = th_decode_headerin(&info, &comment, &setup, &packet);

	      if(theora_result < 0)
		{
		  // Not a valid Theora packet. Stream is not
		  // interesting any more. Don't get more packets from
		  // it. Don't give it more data.

		  if(found_theora_stream)
		    {
		      PyErr_SetString(PyExc_IOError, "Ogg file contains an invalid Theora header");
		      goto clean_up;
		    }

		  killed_streams[stream_index] = 1;
		  break;
		}

	      found_theora_stream = 1;

	      if(theora_result)
		{
		  continue;
		}

	      // All headers done

	      if(info.frame_width > 1920 || info.frame_height > 1080)
		{
		  // Check that the frame size is within
		  // reasonable bounds, to prevent DOS attacks.
		  // 1920x1080 is full HD.
		  PyErr_SetString(PyExc_IOError, "Video frame is too big");
		}

	      decode = th_decode_alloc(&info, setup);

	      if(!decode)
		{
		  PyErr_SetString(PyExc_IOError, "Invalid decoding parameters");
		  goto clean_up;
		}

	      if(th_decode_packetin(decode, &packet, NULL))
		{
		  PyErr_SetString(PyExc_IOError, "Ogg file contains an invalid Theora packet");
		  goto clean_up;
		}

	      result = convert_frame(&info, decode);
	      goto clean_up;
	    }
	}
    }

  // End of loop never reached

 clean_up:
  fclose(file);
  ogg_sync_clear(&sync);

  while(stream_count)
    {
      stream_count--;
      ogg_stream_clear(streams + stream_count);
    }

  if(setup)
    {
      th_setup_free(setup);
    }

  if(decode)
    {
      th_decode_free(decode);
    }

  return result;
}

PyDoc_STRVAR(oggvideopreview_make_preview__doc__,
    "make_preview(path) -> size_x, size_y, aspect_numerator, "
    "aspect_denominator, image_data\n"
    "Create a preview image from an Ogg file containing a Theora stream. "
    "Returns size, pixel aspect ratio and RGB image data of a video frame. May "
    "raise IOError.");

static PyMethodDef oggvideopreview_methods[] = {
  {"make_preview", oggvideopreview_make_preview, METH_VARARGS,
       oggvideopreview_make_preview__doc__},
  {NULL}
};

PyMODINIT_FUNC initoggvideopreview(void)
{
  Py_InitModule("oggvideopreview", oggvideopreview_methods);
}
