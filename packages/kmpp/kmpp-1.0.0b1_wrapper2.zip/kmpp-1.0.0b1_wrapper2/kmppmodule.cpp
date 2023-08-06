#include <Python.h>
#include <numpy/arrayobject.h>
#include "KMeans.h"
// Runs k-means on the given set of points.
//   - n: The number of points in the data set
//   - k: The number of clusters to look for
//   - d: The number of dimensions that the data set lives in
//   - points: An array of size n*d where points[d*i + j] gives coordinate j of point i
//   - attempts: The number of times to independently run k-means with different starting centers.
//               The best result is always returned (as measured by the cost function).
//   - centers: This can either be null or an array of size k*d. In the latter case, it will be
//              filled with the locations of all final cluster centers. Specifically
//              centers[d*i + j] will give coordinate j of center i. If the cluster is unused, it
//              will contain NaN instead.
//   - assignments: This can either be null or an array of size n. In the latter case, it will be
//                  filled with the cluster that each point is assigned to (an integer between 0
//                  and k-1 inclusive).
// The final cost of the clustering is also returned.

//typedef double Scalar;
//Scalar RunKMeansPlusPlus(int n, int k, int d, Scalar *points, int attempts,
//                         Scalar *centers, int *assignments);
static PyObject *
kmpp_RunKMeansPlusPlus(PyObject *self, PyObject *args, PyObject *keywds)
{
	int k;
	int attempts = 1;
	PyObject *points_temp_pyo = NULL;
  //  if (!PyArg_ParseTuple(args, "Oii", 
		//&points_temp_pyo, &k, &attempts))
		//return NULL;
	static char *kwlist[] = {"points", "n_clusters", "n_attempts", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, keywds, "Oi|i", kwlist,
		&points_temp_pyo, &k, &attempts))
		return NULL;

	PyObject *points_pyo = PyArray_FROM_OTF(points_temp_pyo, NPY_DOUBLE, NPY_IN_ARRAY);
    if (points_pyo == NULL) return NULL;
	int n, d;
	{
		int nd = PyArray_NDIM(points_pyo);
		if (nd != 2) goto fail;
		npy_intp *dims = PyArray_DIMS(points_pyo);
		n = dims[0];
		d = dims[1];
	}
	PyObject *centers_pyo;
	{
		const int nd = 2;
		npy_intp dims[nd];
		dims[0] = k;
		dims[1] = d;
		centers_pyo = PyArray_SimpleNew(nd, dims, NPY_DOUBLE);
	}
	PyObject *assignments_pyo;
	{
		const int nd = 1;
		npy_intp dims[nd];
		dims[0] = n;
		assignments_pyo = PyArray_SimpleNew(nd, dims, NPY_INT);
	}
	Scalar *points = (Scalar *)PyArray_DATA(points_pyo);
	Scalar *centers = (Scalar *)PyArray_DATA(centers_pyo);
	int *assignments = (int *)PyArray_DATA(assignments_pyo);
	Scalar cost = RunKMeansPlusPlus(
		n, k, d, points, attempts, 
		centers, assignments);
	Py_DECREF(points_pyo);
	return Py_BuildValue("fOO", cost, centers_pyo, assignments_pyo);
 fail:
    Py_DECREF(points);
    return NULL;
}

static PyMethodDef mymethods[] = {
    { "run", (PyCFunction)kmpp_RunKMeansPlusPlus,
      METH_VARARGS | METH_KEYWORDS,
      "Calculate k-means++ clustering of samples.\n\
	  \n\
	  :param points: A **double** valued numpy.dnarray matrix where each row is a sample point.\n\
	  :param n_clusters: The number of clusters *points* is to be clustered into.\n\
	  :param n_attempts: Number of non-deterministic attempts to find lowest *cost*.\n\
	  :return cost, centers, assignments: *cost* is the cost of the solution.\n\
	  See also scipy.cluster.vq - K-means Clustering and Vector Quantization Module\n"},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

PyMODINIT_FUNC
initkmpp(void)
{
   (void)Py_InitModule("kmpp", mymethods);
   import_array();
}
