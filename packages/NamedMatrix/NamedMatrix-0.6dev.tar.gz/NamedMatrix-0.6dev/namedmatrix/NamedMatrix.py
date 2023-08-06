"""
NamedMatrix.py
@project: Pharmaduke
@author: Nicholas P. Tatonetti
@author: Guy H. Fernald
@created: 11/24/2009
"""
import csv
import sys
import numpy
import maxdot
from StringIO import StringIO

H5PY_SUPPORT = True
try:
    import h5py
except ImportError:
    H5PY_SUPPORT = False

def median(values):
    values = sorted(values)
    if len(values) % 2 == 1:
        return values[(len(values)+1)/2-1]
    else:
        lower = values[len(values)/2-1]
        upper = values[len(values)/2]
        return float(lower+upper)/2

class NamedMatrix(object):
    """
    A NamedMatrix object.
    Wraps a numpy matrix data object with row and column names.
    """
    def __init__(self, data = None, rownames = None, colnames = None):
        """ 
        @data:      numpy.array or numpy.matrix initilization object.
        @rownames:  list of row names
        @colnames:  list of column names
        """
        if data is None:
            self._data = numpy.matrix(numpy.zeros((len(rownames), len(colnames))))
        else:
            if type(data) is NamedMatrix:
                data = data._data
            
            self._data = numpy.matrix(data)
        
        if rownames is None:
            self.rownames = range(self.size(0))
        else:
            self.rownames = list(rownames)
        if colnames is None:
            self.colnames = range(self.size(1))
        else:
            self.colnames = list(colnames)
        
        # We expect the row and column names to be strings.
        self.rownames = map(str, self.rownames)
        self.colnames = map(str, self.colnames)
        
        self._row_index = None
        self._column_index = None
        # Needed to make NamedMatrix iterable.
        self._iter_position = 0
    
    def row_index(self, row):
        """ Get the row index of the given row id. """
        if self._row_index is None:
            self._row_index = dict()
            for index,rowname in enumerate(self.rownames):
                self._row_index[rowname] = index
        return self._row_index.get(row, None)
    
    def column_index(self, column):
        if self._column_index is None:
            self._column_index = dict()
            for index,colname in enumerate(self.colnames):
                self._column_index[colname] = index
        return self._column_index.get(column, None)
    
    def next(self):
        """ Return the next item when iterating over the NamedMatrix """
        if self._iter_position >= (self.size(0)*self.size(1)):
            self._iter_position = 0
            raise StopIteration
        else:
            i = self._iter_position / self.size(1)
            j = self._iter_position % self.size(1)
            self._iter_position += 1
            return self[i,j]
    
    def __iter__(self):
        """ Included to make object iterable. """
        return self
    
    def size(self, axis = None):
        """ Returns the size of the NamedMatrix"""
        if axis is None:
            return tuple(self._data.shape)
        return self._data.shape[axis]
    
    def __getitem__(self, key):
        """
        Override the [] method.
        """
        rows,cols = key
        if type(rows) is str:
            rows = [rows]
        if type(cols) is str:
            cols = [cols]
        
        if type(cols) is list or type(rows) is list:
            return self._getitem_list(rows, cols)
        
        if type(rows) is int:
            new_rownames = [self.rownames[rows]]
        else: # slice
            new_rownames = self.rownames[rows]
        
        if type(cols) is int:
            new_colnames = [self.colnames[cols]]
        else: # slice
            new_colnames = self.colnames[cols]
        
        if type(cols) is int and type(rows) is int:
            return self._data.__getitem__(key)
        
        return NamedMatrix(self._data.__getitem__(key), new_rownames, new_colnames)
    
    def _getitem_list(self, rows, cols):
        if type(cols) is slice:
            start = cols.start if not cols.start is None else 0
            stop = cols.stop if not cols.stop is None else len(self.colnames)
            step = cols.step if not cols.step is None else 1
            cols = range(start, stop, step)
        elif type(cols) is int:
            cols = [cols]
        elif type(cols) is list:
            cols = filter(lambda x: not x is None,[i if type(i) is int else self.column_index(i) for i in cols])
        
        if type(rows) is slice:
            start = rows.start if not rows.start is None else 0
            stop = rows.stop if not rows.stop is None else len(self.rownames)
            step = rows.step if not rows.step is None else 1
            rows = range(start, stop, step)
        elif type(rows) is int:
            rows = [rows]
        elif type(cols) is list:
            rows = filter(lambda x: not x is None, [i if type(i) is int else self.row_index(i) for i in rows])
        
        if len(cols) == 1 and len(rows) == 1:
            return self._data[cols[0],rows[0]]
        
        new_data = [[self._data[i,j] for j in cols] for i in rows]
        new_rownames = [self.rownames[i] for i in rows]
        new_colnames = [self.colnames[i] for i in cols]
        
        return NamedMatrix(new_data, new_rownames, new_colnames)
    
    def __setitem__(self, key, value):
        """ Override the setter """
        if type(value) is NamedMatrix:
            value = value._data
        
        self._data.__setitem__(key, value)
    
    def transpose(self):
        """
        Return the transpose of the matrix.
        """
        return NamedMatrix(self._data.transpose(), self.colnames, self.rownames)
    
    def t(self):
        """
        Return the transpose of the matrix.
        """
        return self.transpose()
    
    def maxdot(self, other):
        """
        Return the max-dot product of self and other.
        """
        if not self.colnames == other.rownames:
            A = self[:, other.rownames]._data
            B = other[self.colnames, :]._data
        else:
            A = self._data
            B = other._data
        
        if not A.shape[1] == B.shape[0]:
            raise Exception("Cannot multiply matrices shapes do not match: %s, %s" % (A.shape, B.shape))
        
        C = numpy.matrix(numpy.zeros((A.shape[0], B.shape[1])))
        maxdot.maxdot(A, B, C)
        return NamedMatrix(C, self.rownames, other.colnames)
    
    def remove_zero_rows(self):
        absmax = map(abs, self.max(1))
        keep = [i for i in range(self.size(0)) if not absmax[i] == 0]
        return self[keep,:]
    
    def __repr__(self):
        """
        String representation of a NamedMatrix
        """
        a = "NamedMatrix:\n"
        a += '%10s' % ''
        a += '%10s '*len(self.colnames) % tuple(self.colnames) + "\n"
        for i in range(len(self.rownames)):
            a += '%10s ' % self.rownames[i]
            a += '%10.3e,'*len(self.colnames) % tuple(self._data[i,:].tolist()[0]) + "\n"
        return a
    
    def __add__(self, other):
        if not self.rownames == other.rownames:
            raise Exception("Dimension mismatch, rownames must match.")
        if not self.colnames == other.colnames:
            raise Exception("Dimension mismatch, colnames must match.")
        
        return NamedMatrix(self._data + other._data, self.rownames, self.colnames)
    
    def __mul__(self, other):
        if not self.colnames == other.rownames:
            raise Exception("Dimension mismatch, self.columns must equal other.rownames.")
        return NamedMatrix(self._data*other._data, self.rownames, other.colnames)
    
    def __eq__(self, other):
        if not self.rownames == other.rownames:
            return False
        if not self.colnames == other.colnames:
            return False
        if not list(self) == list(other):
            return False
        return True
    
    def argsort(self):
        """ Return the indices that would sort the array """
        return numpy.argsort(self._data)
    
    def median(self, axis):
        """ Return the median element, row-wise, or column-wise """
        if axis == 0:
            return self.t()._row_median().t()
        else:
            return self._row_median()
    
    def _row_median(self):
        medians = []
        for i in range(self.size(0)):
            medians.append(median(self._data[i,:].tolist()[0]))
        medmat = NamedMatrix(None, self.rownames, [0] )
        medmat[:,0] = numpy.matrix(medians).transpose()
        return medmat
    
    def mean(self, axis=None):
        """ Return the mean element, row-wise, or column-wise """
        if axis is None:
            return self._data.mean()
        if axis == 0:
            return NamedMatrix(self._data.mean(0), [0], self.colnames)
        else:
            return NamedMatrix(self._data.mean(1), self.rownames, [0])
    
    def max(self, axis=None):
        """ Return the max element, row-wise, or column-wise """
        if axis is None:
            return self._data.max()
        if axis == 0:
            return NamedMatrix(self._data.max(0), [0], self.colnames)
        else:
            return NamedMatrix(self._data.max(1), self.rownames, [0])
    
    def map(self, fun):
        """
        Map the funtion to each element in the matrix.
        """
        new = NamedMatrix(self._data, self.rownames, self.colnames)
        for i in range(self.size(0)):
            for j in range(self.size(1)):
                new[i,j] = fun(self[i,j])
        return new
    
    # DEPRECATED: Filter has been deprecated. You can now directly index
    # DEPRECATED: the NamedMatrix using row or columns names.
    # DEPRECATED: (eg. A[:,[colname1, colname2, ...]])
    def filter(self, rows = slice(None, None, None), columns = slice(None, None, None)):
        """
        Return a matrix with only the columns and rows that are given.
        """
        print >> sys.stderr, "The filter method has been deprecated. You can now directly " + \
            "index the NamedMatrix using row and column names. (eg. A[:,[colname1, colname2, ...]])"
        return self[rows,columns]
    
    def save_loadable(self, file, label="NA"):
        """
        Saved the NamedMatrix to file in a loadable format.
        """
        if type(file) is str:
            file = open(file,'w')
        writer = csv.writer(file, delimiter=',')
        for i,row_id in enumerate(self.rownames):
            for j,col_id in enumerate(self.colnames):
                writer.writerow([row_id, col_id, self._data[i,j], label])
        file.close()
    
    def save_to_file(self, file, row_labels=True, column_labels=True, transform=None):
        """
        Save the NamedMatrix to the file.
        """
        close_file = False
        
        if type(file) is str:
            file = open(file,'w')
            close_file = True
        
        writer = csv.writer(file, delimiter=',')
        
        if row_labels:
            colnames = ['RowID'] + self.colnames
        else:
            colnames = self.colnames
       
        if column_labels:
            writer.writerow(colnames)
        
        for i in range(self.size(0)):
            row_list = self._data[i,:].tolist()[0]
            if not transform is None:
                row_list = transform(row_list)
            
            if row_labels:
                row = [self.rownames[i]] + row_list
            else:
                row = row_list
        
            writer.writerow(row)
        
        file.flush()
        if close_file:
            file.close()
    
    @staticmethod
    def save_to_hdf5(file, named_matrix):
        """Save named_matrix to an hdf5 file"""
        if not H5PY_SUPPORT:
            raise Exception("You must install the h5py package to use hdf5 file format.")
        
        f5 = h5py.File(file,'w')
        f5['rownames'] = numpy.array(named_matrix.rownames)
        f5['colnames'] = numpy.array(named_matrix.colnames)
        f5['_data'] = named_matrix._data
        f5.close()

    @staticmethod
    def load_from_hdf5(file):
        """Load named_matrix from an hdf5 file"""
        if not H5PY_SUPPORT:
            raise Exception("You must install the h5py package to use hdf5 file format.")
        
        f5 = h5py.File(file,'r')
        d = f5['_data']
        r = f5['rownames']
        c = f5['colnames']
        result = NamedMatrix(d,rownames=r,colnames=c)
        f5.close()
        return result
    
    @staticmethod
    def load_from_matrix_file(file, num_rows, has_header=True, delimiter=','):
        """
        Load a matrix from a file which contains num_rows rows and num_col columns.
        """
        if type(file) is str:
            file = open(file)
        
        reader = csv.reader(file, delimiter=delimiter)
        header = reader.next()
        colnames = header[1:]
        rownames = list()
        
        mat = NamedMatrix(None, range(num_rows), colnames)
        
        for row in reader:
            if not len(row[1:]) == len(colnames):
                raise Exception("Wrong number of columns in row: %d, had %d, expected %d.",
                    (len(rownames), len(row[1:]), len(colnames)))
            mat[len(rownames),:] = map(float, row[1:])
            rownames.append(row[0])
        
        mat.rownames = rownames
        
        if not sorted(rownames) == rownames or not sorted(colnames) == colnames:
            mat = mat[sorted(rownames),sorted(colnames)]
        
        return mat
    
    @staticmethod
    def load_from_file(file, sourcecode = None, has_header=True, delimiter=',', matrix=False):
        """Load a matrix from a file.  Any missing values are assumed to 
           be 0.  The row and column names are sorted and the shape of
           the matrix is determined by the number of rows (1st column)
           number of columns (2nd column).
           
           The optional sourcecode will load data with only that 
           sourcecode.
           
           Example:
            
           id1,id1,value,sourcecode
           p1,p2,0.5,pg
           p2,p3,0.7,db
           p2,p1,0.2,pg"""
        
        if type(file) is str:
            file = open(file)
        
        reader = csv.reader(file, delimiter=delimiter)
        if has_header:
            headers = reader.next()
        values = dict()
        rownames = dict()
        colnames = dict()
        
        if type(sourcecode) is str:
            sourcecode = [sourcecode]
        
        source_warning = False
        for row in reader:
            name1 = row[0]
            name2 = row[1]
            val = 1.0
            source = None
            if len(row) > 2:
                val = row[2]
            if len(row) > 3:
                source = row[3]
            
            if not sourcecode is None and source is None and not source_warning:
                source_warning = True
                print >> sys.stderr, "Loading from source that contains no source codes"
            
            if sourcecode is None or source is None or source in sourcecode:
                if not values.has_key(name1):
                    values[name1] = dict()
                values[name1][name2] = float(val)
                rownames[name1] = True
                colnames[name2] = True
        
        rows = []
        for name1 in sorted(rownames.keys()):
            row = []
            for name2 in sorted(colnames.keys()):
                value = 0
                if values.has_key(name1):
                    if values[name1].has_key(name2):
                        value = values[name1][name2]
                row.append(value)
            rows.append(row)
            
        x = NamedMatrix(rows, sorted(rownames.keys()), sorted(colnames.keys()))
        x.reloadable(True, file, sourcecode, has_header)
        return x
    
    def reloadable(self, flag = None, file_handle = None, sourcecode = None, has_header = None):
        """
        Makes the NamedMatrix reloadable from the file handle.
        """
        if not flag is None:
            self._reloadable = flag
            file_handle.seek(0)
            self._reload_args = {'file':file_handle, 'sourcecode':sourcecode, 'has_header':has_header}
        return self._reloadable
    
    def reload(self):
        """
        Reload the named matrix from file if it is reloadable otherwise throw an exception.
        """
        if not self._reloadable:
            raise Exception("This NamedMatrix is not reloadable.")
        
        y = NamedMatrix.load_from_file(**self._reload_args)
        self._data = y._data
        self.rownames = y.rownames
        self.colnames = y.colnames

def main():
    """Test a few functions"""
    str = """drug1,drug2,value,source
01,p2,0.5,pg
02,p3,0.7,db
03,p3,0.7,db
"""
    print NamedMatrix.load_from_file(StringIO(str),'pg')
    print NamedMatrix.load_from_file(StringIO(str),'db')

if __name__ == '__main__':
    main()
