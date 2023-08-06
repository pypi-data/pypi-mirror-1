#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import sys
import os
import textwrap
import traceback
import cProfile
import pstats
import gc
from coopr.pyomo import *
from coopr.opt.base import SolverFactory
from coopr.opt.parallel import SolverManagerFactory
import pyutilib.services
import pyutilib.misc

filter_excepthook=False

#
# Print information about modeling components supported by Pyomo
#
def print_components(options):
    print ""
    print "----------------------------------------------------------------" 
    print "Pyomo Model Components:"
    print "----------------------------------------------------------------" 
    components = pyomo.model_components()
    index = pyutilib.misc.sort_index(components)
    for i in index:
        print ""
        print " "+components[i][0]
        for line in textwrap.wrap(components[i][1], 59):
            print "    "+line
    print ""
    print "----------------------------------------------------------------" 
    print "Pyomo Virtual Sets:"
    print "----------------------------------------------------------------" 
    pyomo_sets = pyomo.predefined_sets()
    index = pyutilib.misc.sort_index(pyomo_sets)
    for i in index:
        print ""
        print " "+pyomo_sets[i][0]
        print "    "+pyomo_sets[i][1]

#
# Setup Pyomo execution environment
#
def setup_environment(options, args):
    #
    # Disable garbage collection
    #
    if options.disable_gc:
        gc.disable()
    #
    # Setup verbose debugging mode
    #
    pyomo.reset_debugging()
    #
    # Setup debugging for specific Pyomo components
    #
    if options.debug is not None:
       for val in options.debug:
         pyomo.set_debugging( val )
    if options.verbose:
       pyomo.set_debugging("verbose")
    #
    # Setup I/O redirect to a logfile
    #
    if not options.logfile is None:
        pyutilib.misc.setup_redirect(options.logfile)
    #
    # Setup management for temporary files
    #
    if not options.tempdir is None:
        if not os.path.exists(options.tempdir):
            raise ValueError, "Directory for temporary files does not exist: "+options.tempdir
        pyutilib.services.TempfileManager.tempdir = options.tempdir
    #
    # Configure exception management
    #
    def pyomo_excepthook(etype,value,tb):
        global filter_excepthook
        model=""
        if len(args) > 0:
            model=args[0]
        print ""
        msg = "ERROR: Unexpected exception while %s %s" % ('loading' if filter_excepthook else 'running', 'model '+model if model != "" else "")
        print msg
        print "  ",value
        print ""
        tb_list = traceback.extract_tb(tb,None)
        i=0
        if not pyomo.debug("all") and filter_excepthook:
            while i < len(tb_list):
                print "Y",model,tb_list[i][0]
                if model in tb_list[i][0]:
                    break
                i += 1
        print "Traceback (most recent call last):"
        for item in tb_list[i:]:
            print "  File \""+item[0]+"\", line "+str(item[1])+", in "+item[2]
            if item[3] is not None:
                print "    "+item[3]
        sys.exit(1)
    sys.excepthook = pyomo_excepthook
    return True

#
# Execute preprocessing files
#
def apply_preprocessing(options, parser, args):
    #
    #
    # Setup solver and model
    #
    #
    if len(args) == 0:
        parser.print_help()
        return False
    #
    for file in options.preprocess:
        preprocess = pyutilib.misc.import_file(file)
    return True
        
#
# Create instance of Pyomo model
#
def create_model(options, args):
    global filter_excepthook
    #
    # Verify that files exist
    #
    for file in args:
        if not os.path.exists(file):
            raise IOError, "File "+file+" does not exist!"
    #
    # Create Model
    #
    filter_excepthook=True
    usermodel = pyutilib.misc.import_file(args[0])
    filter_excepthook=False
    if options.model_name in dir(usermodel):
        model = getattr(usermodel, options.model_name)
        if model is None:
            print ""
            raise SystemExit, "'%s' object equals 'None' in module %s" % (options.model_name, args[0])
            sys.exit(0)
    elif 'create_model' in dir(usermodel):
        model = getattr(usermodel, 'create_model')( pyutilib.misc.Container(*options.model_options) )
    else:
       print ""
       raise SystemExit, "Neither '%s' nor 'create_model' are available in module %s" % (options.model_name,args[0])
       #sys.exit(0)
    #
    # Create Problem Instance
    #
    if len(args) > 2:
        #
        # Load a list of *.dat files
        #
        modeldata = ModelData()
        for file in args[1:]:
            suffix = (file).split(".")[-1]
            if suffix != "dat":
                raise SystemExit, "When specifying multiple data files, they must all be *.dat files: "+str(file)
            modeldata.add_data_file(file)
        modeldata.read(model)
        instance = model.create(modeldata)
         
    elif len(args) == 2:
       #
       # Load a *.dat file or process a *.py data file
       #
       suffix = (args[1]).split(".")[-1]
       if suffix == "dat":
          instance = model.create(args[1])
       elif suffix == "py":
          userdata = pyutilib.misc.import_file(args[1])
          if "modeldata" not in dir(userdata):
             raise SystemExit, "No 'modeldata' object created in module "+args[1]
          if userdata.modeldata is None:
             raise SystemExit, "'modeldata' object equals 'None' in module "+args[1]
          userdata.modeldata.read(model)
          instance = model.create(userdata.modeldata)
       else:
          raise ValueError, "Unknown data file type: "+args[1]
    else:
       instance = model.create()
    if pyomo.debug("instance"):
       print "MODEL INSTANCE"
       instance.pprint()
       print ""

    if not options.save_model is None:
        if options.save_model == True:
            if options.format in [ProblemFormat.cpxlp,ProblemFormat.lpxlp]:
                fname = (args[1])[:-3]+'lp'
            else:
                fname = (args[1])[:-3]+str(options.format)
            format=options.format
        else:
            fname = options.save_model
            format=None
        instance.write(filename=fname, format=format)
        if not os.path.exists(fname):
            print "ERROR: file "+fname+" has not been created!"
        else:
            print "Model written to file '"+str(fname)+"'"

    return instance

#
# Perform optimization with concrete instance
#
def apply_optimizer(options, instance):
    #
    # Create Solver and Perform Optimization
    #
    solver = options.solver
    subsolver=None
    if not solver is None and ':' in solver:
        solver, subsolver = solver.split(':')
    opt = SolverFactory( solver )
    if opt is None:
       raise ValueError, "Problem constructing solver `"+str(solver)+"'"
    opt.keepFiles=options.keepfiles or options.log
    if options.timelimit == 0:
       options.timelimit=None
    if options.solver_mipgap is not None:
       opt.mipgap = options.solver_mipgap
    if not subsolver is None:
        subsolver=' solver='+subsolver
    else:
        subsolver=''
    opt.set_options(" ".join(options.solver_options)+subsolver)
    #
    solver_mngr = SolverManagerFactory( options.smanager_type )
    if solver_mngr is None:
       raise ValueError, "Problem constructing solver manager `"+str(options.smanager_type)+"'"
    results = solver_mngr.solve(instance, opt=opt, tee=options.tee, timelimit=options.timelimit)
    if results == None:
	    raise ValueError, "opt.solve returned None"
    return results, opt

#
# Process results
#
def process_results(options, instance, results, opt):
    
    if options.log:
       print ""
       print "=========================================================="
       print "Solver Logfile:",opt.log_file
       print "=========================================================="
       print ""
       INPUT = open(opt.log_file, "r")
       for line in INPUT:
         print line,
       INPUT.close()
    
    try:
        instance.load(results)
    except Exception, e:
        print "Problem loading solver results"
        raise
    print ""
    results.write(num=1)
    
    if options.summary:
       print ""
       print "=========================================================="
       print "Solution Summary"
       print "=========================================================="
       if len(results.solution(0).variable) > 0:
          print ""
          display(instance)
       else:
          print "No solutions reported by solver."
    return True

def apply_postprocessing(options, instance, results):
    for file in options.postprocess:
        postprocess = pyutilib.misc.import_file(file)
        if "postprocess" in dir(postprocess):
            postprocess.postprocess(instance,results)
        

def run_command(command, parser, args=None, name='unknown'):
    #
    # Execute a function that processes command-line arguments and then
    # calls a command-line driver.  This 
    # is segregated from the driver to enable profiling.
    #

    #
    #
    # Parse command-line options
    #
    #
    try:
       (options, nargs) = parser.parse_args(args=args)
    except SystemExit:
       # the parser throws a system exit if "-h" is specified - catch
       # it to exit gracefully.
       return

    #
    # Call the main Pyomo runner with profiling
    #
    if options.profile > 0:
        tfile = pyutilib.services.TempfileManager.create_tempfile(suffix=".profile")
        tmp = cProfile.runctx(command.__name__+'(options=options,args=nargs,parser=parser)',globals(),locals(),tfile)
        p = pstats.Stats(tfile).strip_dirs()
        p.sort_stats('time', 'cum')
        options.profile = eval(options.profile)
        p = p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        p = p.sort_stats('cum','calls')
        p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        p = p.sort_stats('calls')
        p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        pyutilib.services.TempfileManager.clear_tempfiles()
        ans = [tmp, None]
    else:
        #
        # Call the main Pyomo runner without profiling
        #
        try:
            ans = command(options=options, args=nargs, parser=parser)
        except SystemExit, err:
            if pyomo.debug('errors'):
                sys.exit(0)
            print 'Exiting %s: %s' % (name, str(err))
            ans = None
        except Exception, err:
            if pyomo.debug('errors'):
                raise
            print ""
            print "ERROR:",str(err)
            ans = None

    if options.disable_gc:
        gc.enable()
    return ans

