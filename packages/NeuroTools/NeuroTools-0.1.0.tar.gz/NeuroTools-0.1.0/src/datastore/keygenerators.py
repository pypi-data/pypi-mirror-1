"""
Key generators for data store objects
"""
import hashlib, pickle

def hash_pickle(component):
    """
    Key generator.
    
    Use pickle to convert the component state dictionary to a string, then
    hash this string to give a unique identifier of fixed length.
    """
    state = {'type': component.full_type,
             'version': component.version,
             'parameters_uri': component.parameters.url}
    if component.input is None:
        state['input'] = 'None'
    else:
        state['input'] = hash_pickle(component.input)
    return hashlib.sha1(pickle.dumps(state)).hexdigest()
        
def join_with_underscores(component):
    """
    Key generator.
    
    Return a string that contains all necessary information about the
    component state.
    """
    s = "%s-r%s_%s" % (component.full_type,
                       component.version,
                       component.parameters.url)
    if component.input is not None:
        s += "%s" % join_with_underscores(component.input)
    # remove characters that don't go well in filesystem paths
    replace = lambda s, r: s.replace(r[0],r[1])
    replacements = [('/','_'), (' ','_'), ('[',''), (']',''), (':',''), (',','')]
    s = reduce(replace, [s]+replacements) 
    return s