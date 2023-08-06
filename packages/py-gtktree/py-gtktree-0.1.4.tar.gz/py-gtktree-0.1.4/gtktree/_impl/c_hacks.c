/*--------------------------------------------------------------------------*\
 * This file is part of Py-gtktree.                                         *
 *                                                                          *
 * Copyright (C) 2009 Paul Pogonyshev.                                      *
 *                                                                          *
 * This program is free software: you can redistribute it and/or modify it  *
 * under the terms of the GNU Lesser General Public License as published by *
 * the Free Software Foundation, either version 3 of the License, or (at    *
 * your option) any later version.                                          *
 *                                                                          *
 * This program is distributed in the hope that it will be useful, but      *
 * WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser *
 * General Public License for more details.                                 *
 *                                                                          *
 * You should have received a copy of the GNU Lesser General Public License *
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.    *
\*--------------------------------------------------------------------------*/


#include <Python.h>

#include <pygobject.h>

#include <glib-object.h>
#include <gtk/gtk.h>



/*- Static variables -----------------------------------------------*/

static PyTypeObject *PyGtkTreeModel_Type;
static PyTypeObject *PyGtkTreeIter_Type;



/*- Internal structures --------------------------------------------*/

typedef struct
{
  GtkTreeIterCompareFunc func;
  gpointer               data;
  GDestroyNotify         destroy;
}
TreeIterCompareFuncWrapper;



/*- Internal functions ---------------------------------------------*/

static gboolean
proxy__do_get_sort_column_id (GtkTreeSortable *sortable, gint *sort_column_id, GtkSortType *order)
{
  PyGILState_STATE  py_state = pyg_gil_state_ensure ();
  PyObject         *self    = NULL;
  PyObject         *result  = NULL;
  int               order_;

  *sort_column_id = GTK_TREE_SORTABLE_UNSORTED_SORT_COLUMN_ID;
  if (order)
    *order = GTK_SORT_ASCENDING;

  self = pygobject_new (G_OBJECT (sortable));
  if (!self)
    goto error;

  result = PyObject_CallMethod (self, "do_get_sort_column_id", NULL);
  if (!result)
    goto error;

  if (!PyArg_ParseTuple (result, "ii", sort_column_id, &order_))
    goto error;

  if (order)
    *order = order_;

 done:
  Py_XDECREF (self);
  Py_XDECREF (result);
  pyg_gil_state_release (py_state);

  return *sort_column_id >= 0;

 error:
  if (PyErr_Occurred ())
    PyErr_Print ();

  goto done;
}


static PyObject *
TreeIterCompareFuncWrapper_call (PyObject *self, PyObject *arguments, PyObject *keywords)
{
  static char *valid_keywords[] = { "model", "iter1", "iter2", NULL };

  PyObject                   *py_model;
  PyObject                   *py_iter1;
  PyObject                   *py_iter2;
  TreeIterCompareFuncWrapper *wrapper;
  int                         result;

  if (!PyArg_ParseTupleAndKeywords (arguments, keywords, "O!O!O!", valid_keywords,
                                    PyGtkTreeModel_Type, &py_model,
                                    PyGtkTreeIter_Type,  &py_iter1,
                                    PyGtkTreeIter_Type,  &py_iter2))
    return NULL;

  wrapper = (TreeIterCompareFuncWrapper *) PyCObject_AsVoidPtr (self);
  result  = (*wrapper->func) (GTK_TREE_MODEL (((PyGObject *) py_model)->obj),
                              pyg_boxed_get (py_iter1, GtkTreeIter),
                              pyg_boxed_get (py_iter2, GtkTreeIter),
                              wrapper->data);

  return PyInt_FromLong (result);
}

static void
TreeIterCompareFuncWrapper_destroy (void *wrapper_)
{
  TreeIterCompareFuncWrapper *wrapper = (TreeIterCompareFuncWrapper *) wrapper_;

  if (wrapper->destroy)
    (*wrapper->destroy) (wrapper->data);

  g_slice_free (TreeIterCompareFuncWrapper, wrapper);
}


static PyObject *
wrap_tree_iter_compare_func (GtkTreeIterCompareFunc func, gpointer data, GDestroyNotify destroy)
{
  static PyMethodDef wrapper_method
    = { "_iter_compare", (PyCFunction) TreeIterCompareFuncWrapper_call,
        METH_VARARGS | METH_KEYWORDS, NULL };

  TreeIterCompareFuncWrapper *wrapper;
  PyObject                   *py_wrapper;
  PyObject                   *result;

  if (!func)
    {
      if (destroy)
        (*destroy) (data);

      Py_RETURN_NONE;
    }

  wrapper = g_slice_new (TreeIterCompareFuncWrapper);
  wrapper->func    = func;
  wrapper->data    = data;
  wrapper->destroy = destroy;

  py_wrapper = PyCObject_FromVoidPtr (wrapper, TreeIterCompareFuncWrapper_destroy);
  if (!py_wrapper)
    {
      TreeIterCompareFuncWrapper_destroy (wrapper);
      return NULL;
    }

  result = PyCFunction_New (&wrapper_method, py_wrapper);
  Py_DECREF (py_wrapper);

  return result;
}


static void
do_proxy_do_set_sort_func (GtkTreeSortable *sortable,
                           gboolean default_, gint sort_column_id,
                           GtkTreeIterCompareFunc func, gpointer data,
                           GDestroyNotify destroy)
{
  PyGILState_STATE  py_state = pyg_gil_state_ensure ();
  PyObject         *self    = NULL;
  PyObject         *py_func = NULL;
  PyObject         *result  = NULL;

  self = pygobject_new (G_OBJECT (sortable));
  if (!self)
    goto error;

  py_func = wrap_tree_iter_compare_func (func, data, destroy);
  if (!py_func)
    goto error;

  if (default_)
    result = PyObject_CallMethod (self, "do_set_default_sort_func", "O", py_func);
  else
    result = PyObject_CallMethod (self, "do_set_sort_func", "iO", sort_column_id, py_func);

  if (!result)
    goto error;

 done:
  Py_XDECREF (self);
  Py_XDECREF (py_func);
  Py_XDECREF (result);
  
  pyg_gil_state_release (py_state);

  return;

 error:
  if (PyErr_Occurred ())
    PyErr_Print ();

  goto done;
}

static void
proxy__do_set_sort_func (GtkTreeSortable *sortable, gint sort_column_id,
                         GtkTreeIterCompareFunc func, gpointer data,
                         GDestroyNotify destroy)
{
  do_proxy_do_set_sort_func (sortable, FALSE, sort_column_id, func, data, destroy);
}

static void
proxy__do_set_default_sort_func (GtkTreeSortable *sortable,
                                 GtkTreeIterCompareFunc func, gpointer data,
                                 GDestroyNotify destroy)
{
  do_proxy_do_set_sort_func (sortable, TRUE, 0, func, data, destroy);
}



/*- Free-standing module functions ---------------------------------*/

static PyObject *
register_tree_sortable_implementation (PyObject *self, PyObject *arguments)
{
  PyObject *type;

  if (!PyArg_ParseTuple (arguments,
                         "O:gtktree._impl.c_hacks.register_tree_sortable_implementation",
                         &type))
    return NULL;

  GType  gtype = pyg_type_from_object (type);

  if (!g_type_is_a (gtype, GTK_TYPE_TREE_SORTABLE))
    {
      PyErr_Format (PyExc_TypeError, "expected a GtkTreeSortable implementation type, not %s",
                    g_type_name (gtype));
      return NULL;
    }

  GtkTreeSortableIface *iface = g_type_interface_peek (g_type_class_peek (gtype),
                                                       GTK_TYPE_TREE_SORTABLE);

  if (!iface->get_sort_column_id)
    iface->get_sort_column_id = proxy__do_get_sort_column_id;

  if (!iface->set_sort_func)
    iface->set_sort_func = proxy__do_set_sort_func;

  if (!iface->set_default_sort_func)
    iface->set_default_sort_func = proxy__do_set_default_sort_func;

  Py_RETURN_NONE;
}



/*- Module initialization ------------------------------------------*/

static PyMethodDef c_hacks_functions[]
  = { { "register_tree_sortable_implementation",
        register_tree_sortable_implementation,
        METH_VARARGS, NULL },
      { NULL, NULL, 0, NULL } };


PyMODINIT_FUNC
initc_hacks (void)
{
  PyObject *gtk_module;
  PyObject *module;

  /* FIXME: No idea about required version.  Let's just use something
   *        recent enough. */
  pygobject_init (2, 14, 0);

  gtk_module = PyImport_ImportModule ("gtk");
  if (!gtk_module)
    return;

  PyGtkTreeModel_Type = (PyTypeObject *) PyObject_GetAttrString (gtk_module, "TreeModel");
  if (!PyGtkTreeModel_Type)
    {
      PyErr_SetString (PyExc_ImportError, "cannot import gtk.TreeModel");
      return;
    }

  PyGtkTreeIter_Type = (PyTypeObject *) PyObject_GetAttrString (gtk_module, "TreeIter");
  if (!PyGtkTreeIter_Type)
    {
      PyErr_SetString (PyExc_ImportError, "cannot import gtk.TreeIter");
      return;
    }

  module = Py_InitModule ("c_hacks", c_hacks_functions);

  PyModule_AddIntConstant (module,
                           "TREE_SORTABLE_UNSORTED_SORT_COLUMN_ID",
                           GTK_TREE_SORTABLE_UNSORTED_SORT_COLUMN_ID);
  PyModule_AddIntConstant (module,
                           "TREE_SORTABLE_DEFAULT_SORT_COLUMN_ID",
                           GTK_TREE_SORTABLE_DEFAULT_SORT_COLUMN_ID);
}


/*
 * Local variables:
 * coding: utf-8
 * mode: c
 * c-basic-offset: 2
 * indent-tabs-mode: nil
 * fill-column: 90
 * End:
 */
