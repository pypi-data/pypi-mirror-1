"""
NeuroTools
==========

NeuroTools is not a neural simulator, but rather a collection of tools
to support all tasks associated with a neural simulation project which
are not handled by the simulation engine.

For more information see:
http://neuralensemble.org/NeuroTools


Available subpackages
---------------------

NeuroTools functionality is modularized as follows: 

signals    - provides core classes for manipulation of spike trains and analog signals. 
spike2     - offers an easy way for reading data from CED's Spike2 Son files. 
parameters - contains classes for managing large, hierarchical parameter sets. 
analysis   - cross-correlation, tuning curves, frequency spectrum, etc.
stgen      - various stochastic process generators relevant for Neuroscience 
             (OU, poisson, inhomogenous gamma, ...). 
utilities  - miscellaneous stuff, like SRB access.
io         - NeuroTools support for reading and writing of files in various formats. 
plotting   - routines for plotting and visualization.
datastore  - a consistent interface for persistent data storage (e.g. for caching intermediate results).
random     - a set of classes representing statistical distributions

Sub-package specific documentation is available by importing the
sub-package, and requesting help on it:

>>> import NeuroTools.signals
>>> help(NeuroTools.signals)
"""

__all__ = ['analysis', 'parameters', 'plotting', 'signals', 'stgen', 'io', 'datastore', 'utilities', 'spike2', 'random']
__version__ = "0.1.0 (Asynchronous Astrocyte)"

#########################################################
## ALL DEPENDENCIES SHOULD BE GATHERED HERE FOR CLARITY
#########################################################

# The nice thing would be to gathered every non standard
# dependency here, in order to centralize the warning
# messages and the check
dependencies = {'pylab' : {'website' : 'http://matplotlib.sourceforge.net/', 'is_present' : False, 'check':False},
                'tables': {'website' : 'http://www.pytables.org/moin' , 'is_present' : False, 'check':False},
                'psyco' : {'website' : 'http://psyco.sourceforge.net/', 'is_present' : False, 'check':False},
                'pygsl' : {'website' : 'http://pygsl.sourceforge.net/', 'is_present' : False, 'check':False},
                'PIL'   : {'website' : 'http://www.pythonware.com/products/pil/', 'is_present':False, 'check':False},
                'scipy' : {'website' : 'http://numpy.scipy.org/' , 'is_present' : False, 'check':False},
                'NeuroTools.facets.hdf5' : {'website' : None, 'is_present' : False, 'check':False},
                'srblib' : {'website' : 'http://www.sdsc.edu/srb/index.php/Python', 'is_present' : False, 'check':False},
                'rpy' : {'website' : 'http://rpy.sourceforge.net/', 'is_present' : False, 'check':False},

                ## Add here your extensions ###
               }


#########################################################
## Function to display error messages on the dependencies
#########################################################

def get_warning(name):
    return ''' ----------------- Dependency Warning ---------------------
** %s ** package is not installed. 
To have functions using %s please install the package.
website : %s
''' %(name, name, dependencies[name]['website'])

def check_numpy_version():
    import numpy
    numpy_version = numpy.__version__.split(".")[0:2]
    numpy_version = float(".".join(numpy_version))
    if numpy_version >= 1.2:
        return True
    else:
        return False

def check_pytables_version():
   #v = [int(s) for s in __version__.split('.')]
   if tables.__version__<= 2: #1.4: #v[0] < 1 or (v[0] == 1 and v[1] < 4):
       raise Exception('PyTables version must be >= 1.4, installed version is %s' % __version__)

def check_dependency(name):
    if dependencies[name]['check']:
        return dependencies[name]['is_present']
    else:
        try:
            exec("import %s" %name)
            dependencies[name]['is_present'] = True
        except ImportError:
            print get_warning(name)
        dependencies[name]['check'] = True
        return dependencies[name]['is_present']



# Setup fancy logging

red     = 0010; green  = 0020; yellow = 0030; blue = 0040;
magenta = 0050; cyan   = 0060; bright = 0100
try:
    import ll.ansistyle
    def colour(col,text):
        return str(ll.ansistyle.Text(col,str(text)))
except ImportError:
    def colour(col,text):
            return text
        
import logging

# Add a header() level to logging
logging.HEADER = 60
logging.addLevelName(logging.HEADER, 'HEADER')

root = logging.getLogger()

def root_header(msg, *args, **kwargs):
    if len(root.handlers) == 0:
        basicConfig()
    apply(root.header, (msg,)+args, kwargs)

def logger_header(self, msg, *args, **kwargs):
    if self.manager.disable >= logging.HEADER:
        return
    if logging.HEADER >= self.getEffectiveLevel():
        apply(self._log, (logging.HEADER, msg, args), kwargs)

logging.Logger.header = logger_header
logging.header = root_header

class FancyFormatter(logging.Formatter):
    """
    A log formatter that colours and indents the log message depending on the level.
    """
    
    DEFAULT_COLOURS = {
        'CRITICAL': bright+red,
        'ERROR': red,
        'WARNING': magenta,
        'HEADER': bright+yellow,
        'INFO': cyan,
        'DEBUG': green
    }
    
    DEFAULT_INDENTS = {
        'CRITICAL': "",
        'ERROR': "",
        'WARNING': "",
        'HEADER': "",
        'INFO': "  ",
        'DEBUG': "    ",
    }
    
    def __init__(self, fmt=None, datefmt=None, colours=DEFAULT_COLOURS):
        logging.Formatter.__init__(self, fmt, datefmt)
        self._colours = colours
        self._indents = FancyFormatter.DEFAULT_INDENTS
    
    def format(self, record):
        s = logging.Formatter.format(self, record)
        if record.levelname == "HEADER":
            s = "=== %s ===" % s
        if self._colours:
            s = colour(self._colours[record.levelname], s)
        return self._indents[record.levelname] + s


def init_logging(filename, file_level=logging.INFO, console_level=logging.WARNING):
    logging.basicConfig(level=file_level,
                        format='%(asctime)s %(levelname)s %(message)s', # %(pathname)s %(module)s %(funcName)s',
                        filename=filename,
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(console_level)
    console.setFormatter(FancyFormatter('%(message)s'))
    logging.getLogger('').addHandler(console)
