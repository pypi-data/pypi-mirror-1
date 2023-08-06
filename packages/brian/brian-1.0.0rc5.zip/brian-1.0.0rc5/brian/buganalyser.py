# ----------------------------------------------------------------------------------
# Copyright ENS, INRIA, CNRS
# Contributors: Romain Brette (brette@di.ens.fr) and Dan Goodman (goodman@di.ens.fr)
# 
# Brian is a computer program whose purpose is to simulate models
# of biological neural networks.
# 
# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use, 
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info". 
# 
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability. 
# 
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or 
# data to be ensured and,  more generally, to use and operate it in the 
# same conditions as regards security. 
# 
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
# ----------------------------------------------------------------------------------
# 
"""
Bug analyser for Brian
"""
import sys
import inspect
import re
import stdunits
# Note that the decorator module below is used to provide signature preserving
# decorators, but it has the unfortunate side effect of messing up the tracebacks
# because it uses eval, so we only use it when we want to generate documentation,
# i.e. if 'sphinx' or 'docutils' or 'epydoc' are loaded.
try:
    import decorator
    use_decorator = 'sphinx' in sys.modules or 'docutils' in sys.modules or 'epydoc' in sys.modules
except:
    use_decorator = False

__all__ = [ 'buganalyse', 'analyse_bugs', 'traceback_info' ]

# A list of items of the form (desc, expr) or (desc, expr, flags)
# If regexp groups are defined they will be printed each on a separate line
# see find_regexp_based_error function below for details on groups
simple_regexp_bugs = [
        ("Scipy imported after Brian, may cause function name shadowing.",
             "(from brian import \*).*(from scipy import \*)",
             re.DOTALL),
        ("Numpy imported after Brian, may cause function name shadowing.",
             "(from brian import \*).*(from numpy import \*)",
             re.DOTALL)
        ]
# You can also define more complicated bug finding routines by starting the
# function name in this module with with bug_finder (see below for examples)

def write(*args):
    for arg in args:
        sys.stderr.write(str(arg))
    sys.stderr.write('\n')

def find_one_liner(text,searchtext):
    textlines = text.split('\n')
    one_line_instances = []
    if isinstance(searchtext,str):
        searchtext = [searchtext]
    for i, line in enumerate(textlines):
        for st in searchtext:
            if st in line:
                one_line_instances.append((i,line))
    return one_line_instances

def find_regexp_based_error(expr,text,**opts):
    '''
    Searches for the regular expression expr in text and returns a list of matched lines and line numbers
    
    The return format is a list of items of the form (linenumber_start, linenumber_end, matched_text). If
    the regexp has groups defined, one of these items will be returned for each group in each
    non-overlapping match of the regular expression, otherwise one item will be returned for each match.
    '''
    results = list(re.finditer(expr,text,**opts))
    errors_found = []
    if len(results):
        for match in results:
            groups = match.groups()
            if not len(groups):
                lineno_start = text[:match.start()].count('\n')+1
                lineno_end = text[:match.end()].count('\n')+1
                matched = text[match.start():match.end()]
                errors_found.append((lineno_start,lineno_end,matched))
            else:
                for gi, g in enumerate(groups):
                    if g is not None:
                        lineno_start = text[:match.start(gi+1)].count('\n')+1
                        lineno_end = text[:match.end(gi+1)].count('\n')+1
                        matched = g
                        errors_found.append((lineno_start,lineno_end,matched))
    if len(errors_found)==0:
        errors_found = None
    return errors_found

def simple_bug_finder(bfdef):
    if len(bfdef)==2:
        desc, expr = bfdef
        def f(text):
            return (desc, find_regexp_based_error(expr,text))
    else:
        desc, expr, flags = bfdef
        def f(text):
            return (desc, find_regexp_based_error(expr,text,flags=flags))
    return f

def simple_bug_finders():
    for bfdef in simple_regexp_bugs:
        yield simple_bug_finder(bfdef)

def bug_finder_unit_name_shadowing(text):
    expr = '|'.join([ '[^a-zA-Z_]('+name+' *=.*)' for name in dir(stdunits) if name[:1]!='_' ])
    errors = find_regexp_based_error(expr,text)
    return ('Possible shadowing of short unit names.',errors)

def buganalyse(startlevel=1,verbose=False,additional_bug_funcs=None):
    """
    Analyse the file of the caller.
    """

    write('Brian automatic bug analyser')
    write('============================')
    write('')
    
    found_some_possible_bugs = False
    
    bug_functions = [globals()[_] for _ in globals() if _[:10]=='bug_finder' and callable(globals()[_])]
    bug_functions.extend([f for f in simple_bug_finders()])
    if additional_bug_funcs is not None:
        bug_functions.extend(additional_bug_funcs)
    
    stack = inspect.stack()
    for level in range(startlevel,len(stack)):
        try:
            text=open(stack[level][1]).read()
            done_this_file = False
            for bug_func in bug_functions:
                desc, insts = bug_func(text)
                if insts is not None and len(insts):
                    found_some_possible_bugs = True
                    if not done_this_file:
                        if verbose:
                            write('Analysing this code')
                            write('*******************')
                            write('')
                            write('From file: ',stack[level][1])
                            write('')
                            write(text)
                            write('')
                            write('Possible diagnoses')
                            write('------------------')
                            write('')
                        else:
                            write('From file: ',stack[level][1])
                            write('')
                    done_this_file = True
                    write(desc)
                    for lineno_start, lineno_end, inst in insts:
                        if lineno_start==lineno_end:
                            write('  Line '+str(lineno_start)+': '+inst)
                        else:
                            write('  Lines '+str(lineno_start)+'-'+str(lineno_end)+':\n'+inst)
                    write('')
        except IOError:
            # presumably running from an IPython console or some such
            pass
    if not found_some_possible_bugs:
        write("No suggestions I'm afraid.")
        write('')

# decorator
def analyse_bugs(f):
    def new_f(*args,**kwds):
        try:
            return f(*args,**kwds)
        except:
            try:
                buganalyse()
            except:
                pass
            raise
    new_f.__name__ = f.__name__
    new_f.__doc__ = f.__doc__
    if hasattr(f,'__dict__'):
        new_f.__dict__.update(f.__dict__)
    return new_f

# decorator
def traceback_info(desc):
    def traceback_info_factory(f):
        def new_f(*args,**kwds):
            try:
                return f(*args,**kwds)
            except:
                exc_class, exc, tb = sys.exc_info()
                s = str(exc or exc_class)
                if hasattr(exc_class,'__name__'):
                    s = exc_class.__name__+': ' + s
                new_exc = Exception(desc+'\nOriginal exception was '+s)
                raise new_exc.__class__, new_exc, tb
        new_f.__name__ = f.__name__
        new_f.__doc__ = f.__doc__
        if hasattr(f,'__dict__'):
            new_f.__dict__.update(f.__dict__)
        return new_f
    return traceback_info_factory

# Note: do not normally call this, see note on importing of decorator module at the top of this module
if use_decorator:
    old_analyse_bugs = analyse_bugs
    old_traceback_info = traceback_info
    def analyse_bugs(f):
        return decorator.new_wrapper(old_analyse_bugs(f), f)
    def traceback_info(desc):
        return lambda f : decorator.new_wrapper(old_traceback_info(desc)(f), f)
    analyse_bugs.__doc__ = old_analyse_bugs.__doc__
    traceback_info.__doc__ = old_traceback_info.__doc__
