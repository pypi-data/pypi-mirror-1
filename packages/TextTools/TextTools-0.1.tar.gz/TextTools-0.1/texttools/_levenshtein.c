/*
 * Copyright (c) 2006 Damien Miller <djm@mindrot.org>
 *
 * Permission to use, copy, modify, and distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 * OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 */

/*
 * Adapted for TextTools
 *
 */

#include <sys/types.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#include "Python.h"

#if defined(_MSC_VER)
typedef unsigned __int8 u_int8_t;
#endif

#ifndef MIN
# define MIN(a, b) (((a) < (b)) ? (a) : (b))
#endif

static int _distance(const u_int8_t *a, size_t alen, const u_int8_t *b,
                     size_t blen) {
    size_t tmplen, i, j;
    const u_int8_t *tmp;
    int *current, *previous, *tmpl, add, del, chg, r;

    /* Swap to reduce worst-case memory requirement */
    if (alen > blen) {
        tmp = a;
        a = b;
        b = tmp;
        tmplen = alen;
        alen = blen;
        blen = tmplen;
    }

    if (alen == 0)
        return (blen);

    if ((previous = calloc(alen + 1, sizeof(*previous))) == NULL)
        return (-1);
    if ((current = calloc(alen + 1, sizeof(*current))) == NULL) {
        free(current);
        return (-1);
    }

    for (i = 0; i < alen + 1; i++)
        previous[i] = i;

    for (i = 1; i < blen + 1; i++) {
        if (i > 1) {
            memset(previous, 0, (alen + 1) * sizeof(*previous));
            tmpl = previous;
            previous = current;
            current = tmpl;
        }
        current[0] = i;
        for (j = 1; j < alen + 1; j++) {
            add = previous[j] + 1;
            del = current[j - 1] + 1;
            chg = previous[j - 1];
            if (a[j - 1] != b[i - 1])
                chg++;
            current[j] = MIN(add, del);
            current[j] = MIN(current[j], chg);
        }
    }
    r = current[alen];
    free(previous);
    free(current);
    return (r);
}

PyDoc_STRVAR(distance_doc,
"distance(a, b) -> int\n\n\
    Calculates Levenshtein's edit distance between strings \"a\" and \"b\"\n");

static PyObject *distance(PyObject *self, PyObject *args) {
    char *a, *b;
    int alen, blen, r;

    if (!PyArg_ParseTuple(args, "s#s#", &a, &alen, &b, &blen))
                return NULL;
    r = _distance(a, alen, b, blen);
    if (r == -1) {
        PyErr_SetString(PyExc_MemoryError, "Out of memory");
        return NULL;
    }
    return PyInt_FromLong(r);
}

static PyMethodDef levenshtein_methods[] = {
    {"edit_distance", (PyCFunction)distance,
     METH_VARARGS, distance_doc},
    {NULL, NULL, 0, NULL }  /* sentinel */
};

PyDoc_STRVAR(module_doc, "Calculate Levenshtein's edit distance.\n");

PyMODINIT_FUNC init_levenshtein(void) {
    PyObject *m;
    m = Py_InitModule3("_levenshtein", levenshtein_methods, module_doc);
}

