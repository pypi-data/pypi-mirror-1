/**
 * Python Extension to calculate the max-dot product.
 * project: Pharmaduke
 * author: Nicholas P. Tatonetti
**/

#include "Python.h"
#include "numpy/arrayobject.h"

double **ptrvector(long n)  {
    double **v;
    v=(double **)malloc((size_t) (n*sizeof(double)));
    if (!v)   {
        printf("In **ptrvector. Allocation of memory for double array failed.");
        exit(0);
    }
    return v;
}

void free_Carrayptrs(double **v)  {
     free((char*) v);
}

double **pymatrix_to_Carrayptrs(PyArrayObject *arrayin)  {
    double **c, *a;
    int i,n,m;
    n=arrayin->dimensions[0];
    m=arrayin->dimensions[1];
    c=ptrvector(n);
    a=(double *) arrayin->data;  /* pointer to arrayin data as double */
    for ( i=0; i<n; i++)  {
        c[i]=a+i*m;  }
    return c;
}

int not_doublematrix(PyArrayObject *mat) { 
   if (mat->descr->type_num != NPY_DOUBLE || mat->nd != 2) {
      PyErr_SetString(PyExc_ValueError,
         "In not_doublematrix: array must be of type Float and 2 dimensional (n x m).");
      return 1; }
   return 0;
}

int maxdot_maxdot(PyObject *self, PyObject *args)
{
    PyArrayObject *matinA, *matinB, *matout;    // The python objects to be extracted fro the args.
    double **cinA, **cinB, **cout;              // The c matrices to be created to point to the
                                                // python matrices, cin and cout point to matin
                                                // and matout, respectively.
    
    int i,j,n,m,l,k;
    double maxel, prod;
    
    /* Parse tuples separately since args will differ between C fcns */
    if (!PyArg_ParseTuple(args, "O!O!O!", &PyArray_Type, &matinA, &PyArray_Type, &matinB, &PyArray_Type, &matout))
        return NULL;
    if (NULL == matinA)  return NULL;
    if (NULL == matinB)  return NULL;
    if (NULL == matout)  return NULL;
    
    // Check to make sure matrices are 'double' type.
    if (not_doublematrix(matinA)) return NULL;
    if (not_doublematrix(matinB)) return NULL;
    if (not_doublematrix(matout)) return NULL;
    
    cinA = pymatrix_to_Carrayptrs(matinA);
    cinB = pymatrix_to_Carrayptrs(matinB);
    cout = pymatrix_to_Carrayptrs(matout);
    
    n = matinA->dimensions[0];
    m = matinB->dimensions[1];
    
    k = matinA->dimensions[1]; // == matinB->dimensions[0]
    
    maxel = 0;
    prod = 0;
    
    // Peform the max-dot product.
    for ( i=0; i<n; i++) {
        for ( j=0; j<m; j++) {
            maxel = 0;
            for ( l=0; l<k; l++) {
                prod = cinA[i][l]*cinB[l][j];
                if (l == 0 || maxel < prod) {
                    maxel = prod;
                }
            }
            cout[i][j] = maxel;
        }
    }

    free_Carrayptrs(cinA);
    free_Carrayptrs(cinB);
    free_Carrayptrs(cout);
    return Py_BuildValue("i", 1);
}

static char maxdot_maxdot_doc[] = "maxdot(A,B,C)";
static char maxdot_doc[] = "Wrapper module for max dot product.";

static PyMethodDef maxdot_methods[] = {
    {"maxdot",
    maxdot_maxdot,
    METH_VARARGS,
    maxdot_maxdot_doc},
    {NULL, NULL}
};

void initmaxdot()
{
    Py_InitModule3("maxdot", maxdot_methods, maxdot_doc);
    import_array();
}

