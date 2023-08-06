"""
Defines classes and functions for managing recordings (spikes, membrane
potential etc).

These classes and functions are not part of the PyNN API, and are only for
internal use.

$Id: __init__.py 696 2010-01-18 14:25:32Z apdavison $
"""

import tempfile
import logging
import os.path
import numpy
import os
import files
try:
    from mpi4py import MPI
except ImportError:
    MPI = None

logger = logging.getLogger("PyNN")

numpy1_1_formats = {'spikes': "%g\t%d",
                    'v': "%g\t%g\t%d",
                    'gsyn': "%g\t%g\t%g\t%d"}
numpy1_0_formats = {'spikes': "%g", # only later versions of numpy support different
                    'v': "%g",      # formats for different columns
                    'gsyn': "%g"}

if MPI:
    mpi_comm = MPI.COMM_WORLD
MPI_ROOT = 0

def rename_existing(filename):
    if os.path.exists(filename):
        os.system('mv %s %s_old' % (filename, filename))
        logger.warning("File %s already exists. Renaming the original file to %s_old" % (filename, filename))

def gather(data):
    # gather 1D or 2D numpy arrays
    if MPI is None:
        raise Exception("Trying to gather data without MPI installed. If you are not running a distributed simulation, this is a bug in PyNN.")
    assert isinstance(data, numpy.ndarray)
    assert len(data.shape) < 3
    # first we pass the data size
    size = data.size
    sizes = mpi_comm.gather(size, root=MPI_ROOT) or []
    # now we pass the data
    displacements = [sum(sizes[:i]) for i in range(len(sizes))]
    #print mpi_comm.rank, sizes, displacements, data
    gdata = numpy.empty(sum(sizes))
    mpi_comm.Gatherv([data.flatten(), size, MPI.DOUBLE], [gdata, (sizes,displacements), MPI.DOUBLE], root=MPI_ROOT)
    if len(data.shape) == 1:
        return gdata
    else:
        num_columns = data.shape[1]
        return gdata.reshape((gdata.size/num_columns, num_columns))
  
def gather_dict(D):
    # Note that if the same key exists on multiple nodes, the value from the
    # node with the highest rank will appear in the final dict.
    Ds = mpi_comm.gather(D, root=MPI_ROOT)
    if Ds:
        for otherD in Ds:
            D.update(otherD)
    return D

def mpi_sum(x):
    return mpi_comm.allreduce(x, op=MPI.SUM)


class Recorder(object):
    """Encapsulates data and functions related to recording model variables."""
    

    formats = {'spikes': 'id t',
               'v': 'id t v',
               'gsyn': 'id t ge gi'}
    
    def __init__(self, variable, population=None, file=None):
        """
        Create a recorder.
        
        `variable` -- "spikes", "v" or "gsyn"
        `population` -- the Population instance which is being recorded by the
                        recorder (optional)
        `file` -- one of:
            - a file-name,
            - `None` (write to a temporary file)
            - `False` (write to memory).
        """
        assert variable in Recorder.formats
        self.variable = variable
        self.file = file
        self.population = population # needed for writing header information
        self.recorded = set([])
        
    def record(self, ids):
        """Add the cells in `ids` to the set of recorded cells."""
        logger.debug('Recorder.record(<%d cells>)' % len(ids))
        ids = set([id for id in ids if id.local])
        new_ids = list( ids.difference(self.recorded) )
        self.recorded = self.recorded.union(ids)
        logger.debug('Recorder.recorded contains %d ids' % len(self.recorded))
        self._record(new_ids)
        
    def get(self, gather=False, compatible_output=True):
        """Return the recorded data as a Numpy array."""
        data_array = self._get(gather, compatible_output)
        id_offset = self.population and self.population.first_id or 0
        data_array[:,0] -= id_offset # relies on fact that id is always first column
        self._data_size = data_array.shape[0]
        return data_array
    
    def write(self, file=None, gather=False, compatible_output=True):
        """Write recorded data to file."""
        file = file or self.file
        if isinstance(file, basestring):
            filename = file
            #rename_existing(filename)
            if gather==False and simulator.state.num_processes > 1:
                filename += '.%d' % simulator.state.mpi_rank
        else:
            filename = file.name
        logger.debug("Recorder is writing '%s' to file '%s' with gather=%s and compatible_output=%s" % (self.variable,
                                                                                                        filename,
                                                                                                        gather,
                                                                                                        compatible_output))
        data = self.get(gather, compatible_output)
        metadata = self.metadata
        logger.debug("data has size %s" % str(data.size))
        if simulator.state.mpi_rank == 0 or gather==False:
            if compatible_output:
                data = self._make_compatible(data)
            # Open the output file, if necessary and write the data
            logger.debug("Writing data to file %s" % file)
            if isinstance(file, basestring):
                file = files.StandardTextFile(filename, mode='w')
            file.write(data, metadata)
            file.close()
    
    @property
    def metadata(self):
        metadata = {}
        if self.population is not None:
            metadata.update({
                'dimensions': str(list(self.population.dim)),
                'first_id': 0,
                'last_id': len(self.population)-1
            })
        metadata['dt'] = simulator.state.dt # note that this has to run on all nodes (at least for NEST)
        if not hasattr(self, '_data_size'):
            self.get()
        metadata['n'] = self._data_size
        return metadata
    
    def _make_compatible(self, data_source):
        """
        Rewrite simulation data in a standard format:
            spiketime (in ms) cell_id-min(cell_id)
        """
        assert isinstance(data_source, numpy.ndarray)
        logger.debug("Converting data from memory into compatible format")
        N = len(data_source)
        
        logger.debug("Number of data elements = %d" % N)
        if N > 0:
            # Shuffle columns if necessary
            input_format = self.formats[self.variable].split()
            time_column = input_format.index('t')
            id_column = input_format.index('id')
            
            if self.variable == 'gsyn':
                ge_column = input_format.index('ge')
                gi_column = input_format.index('gi')
                column_map = [ge_column, gi_column, id_column]
            elif self.variable == 'v': # voltage files
                v_column = input_format.index('v')
                column_map = [v_column, id_column]
            elif self.variable == 'spikes': # spike files
                column_map = [time_column, id_column]
            else:
                raise Exception("Invalid variable")
            
            data_array = data_source[:, column_map]
        else:
            logger.warning("%s is empty or does not exist" % data_source)
            data_array = numpy.array([])
        return data_array
    
    def count(self, gather=True):
        """
        Return the number of data points for each cell, as a dict. This is mainly
        useful for spike counts or for variable-time-step integration methods.
        """
        if self.variable == 'spikes':
            N = self._local_count()
        else:
            raise Exception("Only implemented for spikes.")
        if gather and simulator.state.num_processes > 1:
            N = gather_dict(N)
        return N
    
