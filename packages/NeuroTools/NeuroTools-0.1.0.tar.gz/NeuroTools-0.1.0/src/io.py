"""
NeuroTools.io
==================

A collection of functions to handle all the inputs/outputs of the NeuroTools.signals
file, used by the loaders.

Classes
-------

FileHandler        - abstract class which should be overriden, managing how a file will load/write
                     its data
StandardTextFile   - object used to manipulate text representation of NeuroTools objects (spikes or
                     analog signals)
StandardPickleFile - object used to manipulate pickle representation of NeuroTools objects (spikes or
                     analog signals)
DataHandler        - object to establish the interface between NeuroTools.signals and NeuroTools.io

All those objects can be used with NeuroTools.signals

    >> data = StandardTextFile("my_data.dat")
    >> spikes = load(data,'s')
"""


from NeuroTools import check_dependency

import os, logging, cPickle, numpy
DEFAULT_BUFFER_SIZE = 10000


class FileHandler(object):
    """
    Class to handle all the file read/write methods for the key objects of the
    signals class, i.e SpikeList and AnalogSignalList. Could be extented
    
    This is an abstract class that will be implemented for each format (txt, pickle, hdf5)
    The key methods of the class are:
        write(object)              - Write an object to a file
        read_spikes(params)        - Read a SpikeList file with some params
        read_analogs(type, params) - Read an AnalogSignalList of type `type` with some params
    
    Inputs:
        filename - the file name for reading/writing data
    
    If you want to implement your own file format, you just have to create an object that will 
    inherit from this FileHandler class and implement the previous functions. See io.py for more
    details
    """
    
    def __init__(self, filename):
        self.filename = filename
    
    def write(self, object):
        """
        Write the object to the file. 
        
        Examples:
            >> handler.write(SpikeListObject)
            >> handler.write(VmListObject)
        """
        return _abstract_method(self)
    
    def read_spikes(self, params):
        """
        Read a SpikeList object from a file and return the SpikeList object, created from the File and
        from the additional params that may have been provided
        
        Examples:
            >> params = {'id_list' : range(100), 't_stop' : 1000}
            >> handler.read_spikes(params)
                SpikeList Object (with params taken into account)
        """
        return _abstract_method(self)
    
    def read_analogs(self, type, params):
        """
        Read an AnalogSignalList object from a file and return the AnalogSignalList object of type 
        `type`, created from the File and from the additional params that may have been provided
        
        `type` can be in ["vm", "current", "conductance"]
        
        Examples:
            >> params = {'id_list' : range(100), 't_stop' : 1000}
            >> handler.read_analogs("vm", params)
                VmList Object (with params taken into account)
            >> handler.read_analogs("current", params)
                CurrentList Object (with params taken into account)
        """
        if not type in ["vm", "current", "conductance"]:
            raise Exception("The type %s is not available for the Analogs Signals" %type)
        return _abstract_method(self)



class StandardTextFile(FileHandler):
    
    def __init__(self, filename):
        FileHandler.__init__(self, filename)
        self.metadata = {}

    def __read_metadata(self):
        """
        Read the informations that may be contained in the header of
        the NeuroTools object, if saved in a text file
        """
        cmd = ''
        f = open(self.filename, 'r')
        for line in f.readlines():
            if line[0] == '#':
                cmd += line[1:].strip() + ';'
            else:
                break
        f.close()
        exec cmd in None, self.metadata

    def __fill_metadata(self, object):
        """
        Fill the metadata from those of a NeuroTools object before writing the object
        """
        self.metadata['dimensions'] = str(object.dimensions)
        if len(object.id_list() > 0):
            self.metadata['first_id'] = numpy.min(object.id_list())
            self.metadata['last_id']  = numpy.max(object.id_list())
        if hasattr(object, "dt"):
            self.metadata['dt']     = object.dt

    def __check_params(self, params):
        """
        Establish a control/completion/correction of the params to create an object by 
        using comparison and data extracted from the metadata.
        """
        if 'dt' in params:
            if params['dt'] is None and 'dt' in self.metadata:
                logging.debug("dt is infered from the file header")
                params['dt'] = self.metadata['dt']
        if not ('id_list' in params) or (params['id_list'] is None):
            if ('first_id' in self.metadata) and ('last_id' in self.metadata):
                logging.debug("id_list is infered from the file header")
                params['id_list'] = range(int(self.metadata['first_id']), int(self.metadata['last_id'])+1)
            else:
                raise Exception("id_list can not be infered while reading %s" %self.filename)
        elif isinstance(params['id_list'], int): # allows to just specify the number of neurons
            params['id_list'] = range(params['id_list'])
        elif not isinstance(params['id_list'], list):
            raise Exception("id_list should be an int or a list !")
        if not ('dims' in params) or (params['dims'] is None):
            if 'dimensions' in self.metadata:
                params['dims'] = self.metadata['dimensions']
            else:
                raise Exception("dims can not be infered while reading %s" %self.filename)
        return params
            
    def get_data(self, sepchar = "\t", skipchar = "#"):
        """
        Load data from a text file and returns a list of data
        """
        myfile = open(self.filename, "r", DEFAULT_BUFFER_SIZE)
        contents = myfile.readlines()
        myfile.close()
        data = []
        for line in contents:
            line = line.strip()
            if (len(line) != 0):
                if (line[0] != skipchar):
                    line = line.split(sepchar)
                    id    = [int(float(line[-1]))]
                    id.extend(map(float, line[0:-1]))
                    data.append(id)
        return data

    def write(self, object):
        # can we write to the file more than once? In this case, should use seek, tell
        # to always put the header information at the top?
        # write header
        self.__fill_metadata(object)
        fileobj = open(self.filename, 'w', DEFAULT_BUFFER_SIZE)
        header_lines = ["# %s = %s" % item for item in self.metadata.items()]
        fileobj.write("\n".join(header_lines) + '\n')
        numpy.savetxt(fileobj, object.raw_data(), fmt = '%g', delimiter='\t')
        fileobj.close()

    def read_spikes(self, params):
        fileobj = open(self.filename, 'r', DEFAULT_BUFFER_SIZE)
        self.__read_metadata()
        p = self.__check_params(params)
        from NeuroTools import signals
        return signals.SpikeList(self.get_data(), p['id_list'], p['t_start'], p['t_stop'], p['dims'])

    def read_analogs(self, type, params):
        fileobj = open(self.filename, 'r', DEFAULT_BUFFER_SIZE)
        self.__read_metadata()
        p = self.__check_params(params)
        from NeuroTools import signals
        if type == "vm":
            return signals.VmList(self.get_data(), p['id_list'], p['dt'], p['t_start'], p['t_stop'], p['dims'])
        elif type == "current":
            return signals.CurrentList(self.get_data(), p['id_list'], p['dt'], p['t_start'], p['t_stop'], p['dims'])
        elif type == "conductance":
            data  = numpy.array(self.get_data())
            if len(data[0,:]) > 2:
                g_exc = signals.ConductanceList(data[:,[0,1]] , p['id_list'], p['dt'], p['t_start'], p['t_stop'], p['dims'])
                g_inh = signals.ConductanceList(data[:,[0,2]] , p['id_list'], p['dt'], p['t_start'], p['t_stop'], p['dims'])
                return [g_exc, g_inh]
            else:
                return signals.ConductanceList(data, p['id_list'], p['dt'], p['t_start'], p['t_stop'], p['dims'])


class StandardPickleFile(FileHandler):
    
    def __init__(self, filename):
        FileHandler.__init__(self, filename) 
        self.metadata = {}

    def __fill_metadata(self, object):
        """
        Fill the metadata from those of a NeuroTools object before writing the object
        """
        self.metadata['dimensions'] = str(object.dimensions)
        self.metadata['first_id']   = numpy.min(object.id_list())
        self.metadata['last_id']    = numpy.max(object.id_list())
        if hasattr(object, 'dt'):
            self.metadata['dt']     = object.dt

    def __reformat(self, params, object):
        self.__fill_metadata(object)
        if 'id_list' in params and params['id_list'] != None:
            if isinstance(params['id_list'], int): # allows to just specify the number of neurons
                params['id_list'] = range(params['id_list'])
            if params['id_list'] != range(int(self.metadata['first_id']), int(self.metadata['last_id'])+1):
                object = object.id_slice(params['id_list'])
        do_slice = False
        t_start = object.t_start
        t_stop  = object.t_stop
        if 't_start' in params and params['t_start'] is not None and params['t_start'] != object.t_start:
            t_start = params['t_start']
            do_slice = True
        if 't_stop' in params and params['t_stop'] is not None and params['t_stop'] != object.t_stop:
            t_stop = params['t_stop']
            do_slice = True
        if do_slice:
            object = object.time_slice(t_start, t_stop)
        return object
    
    def write(self, object):
        fileobj = file(self.filename,"w")
        return cPickle.dump(object, fileobj)

    def read_spikes(self, params):
        fileobj = file(self.filename,"r")
        object = cPickle.load(fileobj)
        object = self.__reformat(params, object)
        return object
        
    def read_analogs(self, type, params):
        return self.read_spikes(params)


class DataHandler(object):
    """
    Class to establish the interface for loading/saving objects in NeuroTools
    
    Inputs:
        filename - the user file for reading/writing data. By default, if this is
                   string, a StandardTextFile is created
        object   - the object to be saved. Could be a SpikeList or an AnalogSignalList
        
    Examples:
        >> txtfile = StandardTextFile("results.dat")
        >> DataHandler(txtfile)
        >> picklefile = StandardPickelFile("results.dat")
        >> DataHandler(picklefile)
        
    """
    def __init__(self, user_file, object = None):
        if type(user_file) == str:
            user_file = StandardTextFile(user_file)
        elif not isinstance(user_file, FileHandler):
            raise Exception ("The user_file object should be a string or herits from FileHandler !")
        self.user_file     = user_file
        self.object        = object

    def load_spikes(self, **params):
        """
        Function to load a SpikeList object from a file. The data type is automatically
        infered. Return a SpikeList object
        
        Inputs:
            params - a dictionnary with all the parameters used by the SpikeList constructor
        
        Examples:
            >> params = {'id_list' : range(100), 't_stop' : 1000}
            >> handler.load_spikes(params)
                SpikeList object
        
        See also
            SpikeList, load_analogs
        """
        
        ### Here we should have an automatic selection of the correct manager
        ### acccording to the file format.
        ### For the moment, we try the pickle format, and if not working
        ### we assume this is a text file
        return self.user_file.read_spikes(params)


    def load_analogs(self, type, **params):
        """
        Read an AnalogSignalList object from a file and return the AnalogSignalList object of type 
        `type`, created from the File and from the additional params that may have been provided
        
        `type` can be in ["vm", "current", "conductance"]
        
        Examples:
            >> params = {'id_list' : range(100), 't_stop' : 1000}
            >> handler.load_analogs("vm", params)
                VmList Object (with params taken into account)
            >> handler.load_analogs("current", params)
                CurrentList Object (with params taken into account)
        
        See also
            AnalogSignalList, load_spikes
        """
        ### Here we should have an automatic selection of the correct manager
        ### acccording to the file format.
        ### For the moment, we try the pickle format, and if not working
        ### we assume this is a text file
        return self.user_file.read_analogs(type, params)


    def save(self):
        """
        Save the object defined in self.object with the method os self.user_file
        
        Note that you can add your own format for I/O of such NeuroTools objects
        """
        ### Here, you could add your own format if you have created the appropriate
        ### manager.
        ### The methods of the manager are quite simple: should just inherits from the FileHandler
        ### class and have read() / write() methods
        if self.object == None:
            raise Exception("No object has been defined to be saved !")
        else:
            self.user_file.write(self.object)
