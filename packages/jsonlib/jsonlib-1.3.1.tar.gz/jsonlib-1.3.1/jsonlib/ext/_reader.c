/**
 * Copyright (C) 2008 John Millikin. See LICENSE.txt for details.
 * Author: John Millikin <jmillikin@gmail.com>
 * 
 * Implementation of _read in C.
**/

#include "jsonlib-common.h"

typedef struct _ParserState {
	Py_UNICODE *start;
	Py_UNICODE *end;
	Py_UNICODE *index;
	PyObject *Decimal;
	PyObject *ReadError;
} ParserState;

typedef enum
{
	ARRAY_EMPTY,
	ARRAY_NEED_VALUE,
	ARRAY_GOT_VALUE
} ParseArrayState;

typedef enum
{
	OBJECT_EMPTY,
	OBJECT_NEED_KEY,
	OBJECT_GOT_VALUE
} ParseObjectState;

static PyObject *read_keyword (ParserState *state);
static PyObject *read_string (ParserState *state);
static PyObject *read_number (ParserState *state);
static PyObject *read_array (ParserState *state);
static PyObject *read_object (ParserState *state);
static PyObject *json_read (ParserState *state);

static void
skip_spaces (ParserState *state)
{
	/* Don't use Py_UNICODE_ISSPACE, because it returns TRUE for
	 * codepoints that are not valid JSON whitespace.
	**/
	Py_UNICODE c;
	while ((c = (*state->index)) && (
		c == 0x0009 ||
		c == 0x0020 ||
		c == 0x000A ||
		c == 0x000C
	))
		state->index++;
}

static Py_UCS4
next_ucs4 (ParserState *state, Py_UNICODE *index)
{
	unsigned long value = index[0];
	if (value >= 0xD800 && value <= 0xDBFF)
	{
		unsigned long upper = value, lower = index[1];
		
		if (lower)
		{
			upper -= 0xD800;
			lower -= 0xDC00;
			value = ((upper << 10) + lower) + 0x10000;
		}
	}
	return value;
}

static void
count_row_column (Py_UNICODE *start, Py_UNICODE *pos, unsigned long *offset,
                  unsigned long *row, unsigned long *column)
{
	Py_UNICODE *ptr;
	*offset = (pos - start);
	*row = 1;
	
	/* Count newlines in chars <= pos */
	for (ptr = start; ptr && ptr <= pos; ptr++)
	{
		if (*ptr == '\n') (*row)++;
	}
	
	/* Loop backwards to find the column */
	while (ptr > start && *ptr != '\n') ptr--;
	*column = (pos - ptr);
	if (*row == 1) (*column)++;
}

static void
set_error (ParserState *state, Py_UNICODE *position, PyObject *description,
           PyObject *description_args)
{
	const char *tmpl = "JSON parsing error at line %d, column %d"
	                   " (position %d): %s";
	unsigned long row, column, char_offset;
	PyObject *err_str, *err_str_tmpl, *err_format_args;
	
	Py_INCREF (description);
	
	if (description_args)
	{
		PyObject *new_desc;
		new_desc = PyString_Format (description, description_args);
		Py_DECREF (description);
		if (!new_desc) return;
		description = new_desc;
	}
	
	count_row_column (state->start, position, &char_offset,
	                  &row, &column);
	
	err_str_tmpl = PyString_FromString (tmpl);
	if (err_str_tmpl)
	{
		err_format_args = Py_BuildValue ("(kkkO)", row, column,
		                                 char_offset, description);
		if (err_format_args)
		{
			err_str = PyString_Format (err_str_tmpl, err_format_args);
			if (err_str)
			{
				PyErr_SetObject (state->ReadError, err_str);
				Py_DECREF (err_str);
			}
			Py_DECREF (err_format_args);
		}
		Py_DECREF (err_str_tmpl);
	}
	Py_DECREF (description);
}

static void
set_error_simple (ParserState *state, Py_UNICODE *position,
                  const char *description)
{
	PyObject *desc_obj;
	desc_obj = PyString_FromString (description);
	if (desc_obj)
	{
		set_error (state, position, desc_obj, NULL);
		Py_DECREF (desc_obj);
	}
}

static void
set_error_unexpected (ParserState *state, Py_UNICODE *position)
{
	PyObject *err_str, *err_format_args;
	Py_UCS4 c = next_ucs4 (state, position);
	
	if (c > 0xFFFF)
		err_str = PyString_FromString ("Unexpected U+%08X.");
	else
		err_str = PyString_FromString ("Unexpected U+%04X.");
	
	if (err_str)
	{
		err_format_args = Py_BuildValue ("(k)", c);
		if (err_format_args)
		{
			set_error (state, position, err_str, err_format_args);
			Py_DECREF (err_format_args);
		}
		Py_DECREF (err_str);
	}
}

/* Helper function to create a new decimal.Decimal object */
static PyObject *
make_Decimal (ParserState *state, PyObject *string)
{
	PyObject *args, *retval = NULL;
	
	if ((args = PyTuple_Pack (1, string)))
	{
		retval = PyObject_CallObject (state->Decimal, args);
		Py_DECREF (args);
	}
	return retval;
}

/* Helper function to perform strncmp between Py_UNICODE and char* */
static int
unicode_utf8_strncmp (Py_UNICODE *unicode, const char *utf8, Py_ssize_t count)
{
	PyObject *str;
	char *c_str;
	int retval = -1;
	
	str = PyUnicode_EncodeUTF8 (unicode, count, "strict");
	if (str)
	{
		c_str = PyString_AsString (str);
		if (c_str)
		{
			retval = strncmp (c_str, utf8, count);
		}
		Py_DECREF (str);
	}
	
	return retval;
}

static PyObject *
keyword_compare (ParserState *state, const char *expected, PyObject *retval)
{
	size_t left, len = strlen (expected);
	
	left = state->end - state->index;
	
	if (left >= len &&
	    unicode_utf8_strncmp (state->index, expected, len) == 0)
	{
		state->index += len;
		Py_INCREF (retval);
		return retval;
	}
	return NULL;
}

static PyObject *
read_keyword (ParserState *state)
{
	PyObject *retval;
	
	if ((retval = keyword_compare (state, "null", Py_None)))
		return retval;
	if ((retval = keyword_compare (state, "true", Py_True)))
		return retval;
	if ((retval = keyword_compare (state, "false", Py_False)))
		return retval;
	
	set_error_unexpected (state, state->index);
	return NULL;
}

static int
read_4hex (Py_UNICODE *start, Py_UNICODE *retval_ptr)
{
	PyObject *py_long;
	
	py_long = PyLong_FromUnicode (start, 4, 16);
	if (!py_long) return FALSE;
	
	(*retval_ptr) = (Py_UNICODE) (PyLong_AsUnsignedLong (py_long));
	Py_DECREF (py_long);
	return TRUE;
}

static int
read_unicode_escape (ParserState *state, Py_UNICODE *string_start,
                     Py_UNICODE *buffer, Py_ssize_t *buffer_idx,
                     Py_ssize_t *index_ptr, Py_ssize_t max_char_count)
{
	Py_ssize_t remaining;
	Py_UNICODE value;
	
	(*index_ptr)++;
	
	remaining = max_char_count - (*index_ptr);
	
	if (remaining < 4)
	{
		set_error_simple (state, state->index + (*index_ptr) - 1,
		                  "Unterminated unicode escape.");
		return FALSE;
	}
	
	if (!read_4hex (string_start + (*index_ptr), &value))
		return FALSE;
		
	(*index_ptr) += 4;
	
	/* Check for surrogate pair */
	if (0xD800 <= value && value <= 0xDBFF)
	{
		Py_UNICODE upper = value, lower;
		
		if (remaining < 10)
		{
			set_error_simple (state, state->index + (*index_ptr) + 1,
			                  "Missing surrogate pair half.");
			return FALSE;
		}
		
		if (string_start[(*index_ptr)] != '\\' ||
		    string_start[(*index_ptr) + 1] != 'u')
		{
			set_error_simple (state, state->index + (*index_ptr) + 1,
			                  "Missing surrogate pair half.");
			return FALSE;
		}
		(*index_ptr) += 2;
		
		if (!read_4hex (string_start + (*index_ptr), &lower))
			return FALSE;
			
		(*index_ptr) += 4;
		
#		ifdef Py_UNICODE_WIDE
			upper -= 0xD800;
			lower -= 0xDC00;
			
			/* Merge upper and lower components */
			value = ((upper << 10) + lower) + 0x10000;
			buffer[*buffer_idx] = value;
#		else
			/* No wide character support, return surrogate pairs */
			buffer[(*buffer_idx)++] = upper;
			buffer[*buffer_idx] = lower;
#		endif
	}
	else if (0xDC00 <= value && value <= 0xDFFF)
	{
		PyObject *err_str, *err_format_args;
		Py_UNICODE *position = state->index + (*index_ptr) - 5;

		err_str = PyString_FromString ("U+%04X is a reserved code point.");

		if (err_str)
		{
			err_format_args = Py_BuildValue ("(k)", value);
			if (err_format_args)
			{
				set_error (state, position, err_str, err_format_args);
				Py_DECREF (err_format_args);
			}
			Py_DECREF (err_str);
		}
		return FALSE;
	}
	else
	{
		buffer[*buffer_idx] = value;
	}
	return TRUE;
}

static PyObject *
read_string (ParserState *state)
{
	PyObject *unicode;
	int escaped = FALSE;
	Py_UNICODE c, *buffer, *start;
	Py_ssize_t ii, max_char_count, buffer_idx;
	
	/* Start at 1 to skip first double quote. */
	start = state->index + 1;
	
	/* Scan through for maximum character count, and to ensure the string
	 * is terminated.
	**/
	for (ii = 0;; ii++)
	{
		c = start[ii];
		if (c == 0)
		{
			set_error_simple (state, state->index,
			                  "Unterminated string.");
			return NULL;
		}
		
		/* Check for illegal characters */
		if (c < 0x20)
		{
			set_error_unexpected (state, start + ii);
			return NULL;
		}
		
		if (escaped)
		{
			/* Invalid escape codes will be caught
			 * later.
			**/
			escaped = FALSE;
		}
		
		else
		{	if (c == '\\') escaped = TRUE;
			else if (c == '"') break;
		}
	}
	
	/* Allocate enough to hold the worst case */
	max_char_count = ii;
	buffer = PyMem_New (Py_UNICODE, max_char_count);
	
	/* Scan through the string, adding values to the buffer as
	 * appropriate.
	**/
	escaped = FALSE;
	buffer_idx = 0;
	for (ii = 0; ii < max_char_count; ii++)
	{
		c = start[ii];
		assert (c != 0);
		
		if (escaped)
		{
			switch (c)
			{
				case '\\':
				case '"':
				case '/':
					buffer[buffer_idx] = c;
					break;
				case 'b': buffer[buffer_idx] = 0x08; break;
				case 'f': buffer[buffer_idx] = 0x0C; break;
				case 'n': buffer[buffer_idx] = 0x0A; break;
				case 'r': buffer[buffer_idx] = 0x0D; break;
				case 't': buffer[buffer_idx] = 0x09; break;
				case 'u':
				{
					Py_ssize_t next_ii = ii;
					if (read_unicode_escape (state, start,
					                         buffer,
					                         &buffer_idx,
					                         &next_ii,
					                         max_char_count))
					{
						ii = next_ii - 1;
					}
					
					else
					{
						PyMem_Free (buffer);
						return NULL;
					}
					break;
				}
				
				default:
				{
					set_error_simple (state, start + ii - 1,
					                  "Unknown escape code.");
					PyMem_Free (buffer);
					return NULL;
				}
			}
			escaped = FALSE;
			buffer_idx += 1;
		}
		
		else
		{
			if (c == '\\') escaped = TRUE;
			else if (c == '"') break;
			else
			{
				buffer[buffer_idx] = c;
				buffer_idx += 1;
			}
		}
	}
	
	unicode = PyUnicode_FromUnicode (buffer, buffer_idx);
	PyMem_Free (buffer);
	
	if (unicode)
	{
		state->index = start + max_char_count + 1;
	}
	
	return unicode;
}

static PyObject *
read_number (ParserState *state)
{
	PyObject *object = NULL;
	int is_float = FALSE, should_stop = FALSE, got_digit = FALSE,
	    leading_zero = FALSE, has_exponent = FALSE;
	Py_UNICODE *ptr, c;
	
	ptr = state->index;
	
	while ((c = *ptr))
	{
		switch (c) {
		case '0':
			if (!got_digit)
			{
				leading_zero = TRUE;
			}
			else if (leading_zero && !is_float)
			{
				set_error_simple (state, state->index,
				                  "Number with leading zero.");
				return NULL;
			}
			got_digit = TRUE;
			break;
		case '1':
		case '2':
		case '3':
		case '4':
		case '5':
		case '6':
		case '7':
		case '8':
		case '9':
			if (leading_zero && !is_float)
			{
				set_error_simple (state, state->index,
				                  "Number with leading zero.");
				return NULL;
			}
			got_digit = TRUE;
			break;
		case '-':
		case '+':
			break;
		case 'e':
		case 'E':
			has_exponent = TRUE;
			break;
		case '.':
			is_float = TRUE;
			got_digit = FALSE;
			break;
		default:
			should_stop = TRUE;
		}
		if (should_stop) {
			break;
		}
		ptr++;
	}
	
	if (got_digit)
	{
		if (is_float || has_exponent)
		{
			PyObject *str, *unicode;
			if (!(unicode = PyUnicode_FromUnicode (state->index,
			                                      ptr - state->index)))
				return NULL;
			str = PyUnicode_AsUTF8String (unicode);
			Py_DECREF (unicode);
			if (!str) return NULL;
			object = make_Decimal (state, str);
			Py_DECREF (str);
		}
		
		else
		{
			object = PyLong_FromUnicode (state->index,
			                             ptr - state->index, 10);
		}
	}
	
	if (object == NULL)
	{
		set_error_simple (state, state->index, "Invalid number.");
		return NULL;
	}
	
	state->index = ptr;
	return object;
}

static int
read_array_impl (PyObject *list, ParserState *state)
{
	Py_UNICODE *start, c;
	ParseArrayState array_state = ARRAY_EMPTY;
	
	start = state->index;
	state->index++;
	while (TRUE)
	{
		skip_spaces (state);
		c = *state->index;
		if (c == 0)
		{
			set_error_simple (state, state->index,
			                  "Unterminated array.");
			return FALSE;
		}
		
		else if (c == ']')
		{
			if (array_state == ARRAY_NEED_VALUE)
			{
				set_error_simple (state, state->index,
				                  "Expecting array item.");
				return FALSE;
			}
			state->index++;
			return TRUE;
		}
		
		else if (c == ',')
		{
			if (array_state != ARRAY_GOT_VALUE)
			{
				set_error_simple (state, state->index,
				                  "Expecting array item.");
				return FALSE;
			}
			array_state = ARRAY_NEED_VALUE;
			state->index++;
		}
		
		else
		{
			PyObject *value;
			int result;
			
			if (array_state == ARRAY_GOT_VALUE)
			{
				set_error_simple (state, state->index,
				                  "Expecting comma.");
				return FALSE;
			}
			
			if (!(value = json_read (state)))
				return FALSE;
			
			result  = PyList_Append (list, value);
			Py_DECREF (value);
			if (result == -1)
				return FALSE;
			
			array_state = ARRAY_GOT_VALUE;
		}
	}
}

static PyObject *
read_array (ParserState *state)
{
	PyObject *object = PyList_New (0);
	
	if (!read_array_impl (object, state))
	{
		Py_DECREF (object);
		return NULL;
	}
	
	return object;
}

static int
read_object_impl (PyObject *object, ParserState *state)
{
	Py_UNICODE *start, c;
	ParseObjectState object_state = OBJECT_EMPTY;
	
	start = state->index;
	state->index++;
	while (TRUE)
	{
		skip_spaces (state);
		c = *state->index;
		if (c == 0)
		{
			set_error_simple (state, start,
			                  "Unterminated object.");
			return FALSE;
		}
		
		else if (c == '}')
		{
			if (object_state == OBJECT_NEED_KEY)
			{
				set_error_simple (state, state->index,
				                  "Expecting property name.");
				return FALSE;
			}
			state->index++;
			return TRUE;
		}
		
		else if (c == ',')
		{
			if (object_state != OBJECT_GOT_VALUE)
			{
				set_error_simple (state, state->index,
				                  "Expecting property name.");
				return FALSE;
			}
			object_state = OBJECT_NEED_KEY;
			state->index++;
		}
		
		else if (c == '"')
		{
			PyObject *key, *value;
			int result;
			
			if (object_state == OBJECT_GOT_VALUE)
			{
				set_error_simple (state, state->index,
				                  "Expecting comma.");
				return FALSE;
			}
			
			if (!(key = json_read (state)))
				return FALSE;
			
			skip_spaces (state);
			if (*state->index != ':')
			{
				set_error_simple (state, state->index,
				                  "Expected colon after object"
				                  " property name.");
				Py_DECREF (key);
				return FALSE;
			}
			
			state->index++;
			if (!(value = json_read (state)))
			{
				Py_DECREF (key);
				return FALSE;
			}
			
			result = PyDict_SetItem (object, key, value);
			Py_DECREF (key);
			Py_DECREF (value);
			if (result == -1)
				return FALSE;
			
			object_state = OBJECT_GOT_VALUE;
		}
		
		else
		{
			set_error_simple (state, state->index,
			                  "Expecting property name.");
			return FALSE;
		}
	}
}

static PyObject *
read_object (ParserState *state)
{
	PyObject *object = PyDict_New ();
	
	if (!read_object_impl (object, state))
	{
		Py_DECREF (object);
		return NULL;
	}
	
	return object;
}

static PyObject *
json_read (ParserState *state)
{
	skip_spaces (state);
	switch (*state->index)
	{
		case 0:
			set_error_simple (state, state->start,
			                  "No expression found.");
			return NULL;
		case '{':
			return read_object (state);
		case '[':
			return read_array (state);
		case '"':
			return read_string (state);
		case 't':
		case 'f':
		case 'n':
			return read_keyword (state);
		case '-':
		case '0':
		case '1':
		case '2':
		case '3':
		case '4':
		case '5':
		case '6':
		case '7':
		case '8':
		case '9':
			return read_number (state);
		default:
			set_error_unexpected (state, state->index);
			return NULL;
	}
}

static PyObject*
_read_entry (PyObject *self, PyObject *args)
{
	PyObject *result, *unicode;
	ParserState state;
	
	if (!PyArg_ParseTuple (args, "UOO:_read", &unicode,
	                       &state.Decimal, &state.ReadError))
		return NULL;
	
	state.start = PyUnicode_AsUnicode (unicode);
	state.end = state.start + PyUnicode_GetSize (unicode);
	state.index = state.start;
	
	if ((result = json_read (&state)))
	{
		skip_spaces (&state);
		if (state.index < state.end)
		{
			set_error_simple (&state, state.index,
			                  "Extra data after JSON expression.");
			Py_DECREF (result);
			result = NULL;
		}
	}
	
	return result;
}

static PyMethodDef reader_methods[] = {
	{"_read", (PyCFunction) (_read_entry), METH_VARARGS,
	PyDoc_STR ("_read (string) -> Deserialize the JSON expression to\n"
	           "a Python object.")},
	
	{NULL, NULL}
};

PyDoc_STRVAR (module_doc,
	"Fast implementation of jsonlib._read."
);

PyMODINIT_FUNC
init_reader (void)
{
	Py_InitModule3 ("_reader", reader_methods, module_doc);
}
