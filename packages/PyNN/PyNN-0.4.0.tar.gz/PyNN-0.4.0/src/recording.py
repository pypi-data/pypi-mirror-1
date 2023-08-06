"""
Defines classes and functions for managing recordings (spikes, membrane
potential etc).
$Id: recording.py 337 2008-06-05 12:45:40Z apdavison $
"""

import tempfile
import logging
import os.path
import numpy

DEFAULT_BUFFER_SIZE = 10000

class RecordingManager(object):
    
    def __init__(self, setup_function, get_function):
        """
        `setup_function` should take a variable, a source list, and an optional filename
        and return an identifier.
        `get_function` should take the identifier returned by `setup_function` and
        return the recorded spikes, Vm trace, etc.
        
        Example:
        rm = RecordingManager(_nest_record, _nest_get)
        """
        # create temporary directory
        tempdir = tempfile.mkdtemp()
        # initialise mapping from recording identifiers to temporary filenames
        self.recorder_list = []
        # for parallel simulations, determine if this is the master node
        self._setup = setup_function
        self._get = get_function
    
    def add_recording(self, sources, variable, filename=None):
        recorder = self._setup(variable, sources, filename)
        self.recorder_list.append(recorder)
    
    def get_recording(self, recording_id):
        return self._get(recording_id)
    
    def write(self, recording_id, filename_or_obj, format="compatible", gather=True):
        pass


def write_compatible_output(sim_filename, user_filename, population, dt):
    """
    Rewrite simulation data in a standard format:
        spiketime (in ms) cell_id-min(cell_id)
    """
    logging.info("Writing %s in compatible format (was %s)" % (user_filename, sim_filename))
    result = open(user_filename,'w',DEFAULT_BUFFER_SIZE)
        
    # Write header info (e.g., dimensions of the population)
    if population is not None:
        result.write("# dimensions =" + "\t".join([str(d) for d in population.dim]) + "\n")
        result.write("# first_id = %d\n" % population.id_start)
        result.write("# last_id = %d\n" % (population.id_start+len(population)-1,))
        padding = population.id_start
    else:
        padding = 0
    result.write("# dt = %g\n" % dt)
                    
    # Writing spiketimes, cell_id-min(cell_id)                    
    # open file
    if os.path.getsize(sim_filename) > 0:
        data = readArray(sim_filename, sepchar=None)
        data[:,0] = data[:,0] - padding
        # sort
        #indx = data.argsort(axis=0, kind='mergesort')[:,0] # will quicksort (not stable) work?
        #data = data[indx]
        if data.shape[1] == 4: # conductance files
            raise Exception("Not yet implemented")
        elif data.shape[1] == 3: # voltage files
            #result.write("# n = %d\n" % int(nest.GetStatus([0], "time")[0]/dt))
            result.write("# n = %d\n" % len(data))
            for idx in xrange(len(data)):
                result.write("%g\t%d\n" % (data[idx][2], data[idx][0])) # v id
        elif data.shape[1] == 2: # spike files
            for idx in xrange(len(data)):
                result.write("%g\t%d\n" % (data[idx][1], data[idx][0])) # time id
        else:
            raise Exception("Data file should have 2,3 or 4 columns, actually has %d" % data.shape[1])
    else:
        logging.info("%s is empty" % sim_filename)
    result.close()


def readArray(filename, sepchar=None, skipchar='#'):
    """
    (Pylab has a great load() function, but it is not necessary to import
    it into pyNN. The fromfile() function of numpy has trouble on several
    machines with Python 2.5, so that's why a dedicated readArray function
    has been created to load from file the spike raster or the membrane potentials
    saved by the simulators).
    """
    logging.debug(filename)
    myfile = open(filename, "r", DEFAULT_BUFFER_SIZE)
    contents = myfile.readlines()
    myfile.close()
    logging.debug(contents)
    data = []
    for line in contents:
        stripped_line = line.lstrip()
        if (len(stripped_line) != 0):
            if (stripped_line[0] != skipchar):
                items = stripped_line.split(sepchar)
                data.append(map(float, items))
    a = numpy.array(data)
    if a.size > 0:
        (Nrow, Ncol) = a.shape
        logging.debug(str(a.shape))
        #if ((Nrow == 1) or (Ncol == 1)): a = numpy.ravel(a)
    return a
