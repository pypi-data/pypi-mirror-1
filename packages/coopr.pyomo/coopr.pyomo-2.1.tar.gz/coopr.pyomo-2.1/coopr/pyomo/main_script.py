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
from optparse import OptionParser
#
# Finish imports
#
from coopr.pyomo import *
from coopr.opt.base import SolverFactory
from coopr.opt.parallel import SolverManagerFactory
import pyutilib.services
import pyutilib.misc
import textwrap
import traceback
import cProfile
import pstats
import gc

#
#
# Setup command-line options
#
#
solver_help=\
"This option specifies the type of solver that is used "\
"to solve the Pyomo model instance.  The following solver "\
"types are are currently supported:"
_tmp = SolverFactory()
_tmp.sort()
for item in _tmp:
  if item[0] != "_":
     solver_help += "\n.."+item
solver_help += ".\nThe default solver is 'glpk'."
debug_help=\
"This option is used to turn on debugging output. This option "\
"can be specified multiple times to turn on different debugging"\
"output. The following debugging options can be specified:"
debug_choices=[]
for item in pyomo.Debug:
  if str(item) != "none":
     debug_choices.append( str(item) )
     debug_help += "\n.."+str(item)

parser = OptionParser()
parser.add_option("--solver",
    help=solver_help,
    action="store",
    dest="solver",
    type="string",
    default="glpk")
parser.add_option("--path",
    help="Give a path that is used to find the Pyomo python files",
    action="store",
    dest="path",
    type="string",
    default=".")
parser.add_option("--help-components",
        help="Print information about modeling components supported by Pyomo",
        action="store_true",
        dest="help_components",
        default=False)
parser.add_option("--debug",
        help=debug_help,
        action="append",
        dest="debug",
        choices=debug_choices)
parser.add_option("-k","--keepfiles",
        help="Keep temporary files",
        action="store_true",
        dest="keepfiles",
        default=False)
parser.add_option("--tempdir",
        help="Specify the directory where temporary files are generated",
        action="store",
        dest="tempdir",
        default=None)
parser.add_option("-q","--quiet",
        help="Turn off solver output",
        action="store_true",
        dest="quiet",
        default=False)
parser.add_option("-l","--log",
        help="Print the solver logfile after performing optimization",
        action="store_true",
        dest="log",
        default=False)
parser.add_option("--logfile",
        help="Redirect output to the specified logfile",
        action="store",
        dest="logfile",
        default=None)
parser.add_option("-s","--summary",
        help="Summarize the final solution after performing optimization",
        action="store_true",
        dest="summary",
        default=False)
parser.add_option("--instance-only",
        help="Generate a model instance, and then return",
        action="store_true",
        dest="only_instance",
        default=False)
parser.add_option("--profile",
        help="Enable profiling of Python code.  The value of this option is the number of functions that are summarized.",
        action="store",
        dest="profile",
        default=0)
parser.add_option("--timelimit",
        help="Limit to the number of seconds that the solver is run",
        action="store",
        dest="timelimit",
        type="int",
        default=0)
parser.add_option("--postprocess",
        help="Specify a Python module that gets executed after optimization.  If this option is specified multiple times, then the modules are executed in the specified order.",
        action="append",
        dest="postprocess",
        default=[])
parser.add_option("--preprocess",
        help="Specify a Python module that gets immediately executed (before the optimization model is setup).  If this option is specified multiple times, then the modules are executed in the specified order.",
        action="append",
        dest="preprocess",
        default=[])
parser.add_option("-v","--verbose",
        help="Make solver output verbose",
        action="store_true",
        dest="verbose",
        default=False)
parser.add_option("--solver-options",
        help="Options passed into the solver",
        action="append",
        dest="solver_options",
        type="string",
        default=[])
parser.add_option("--solver-mipgap",
        help="The solver termination mipgap",
        action="store",
        dest="solver_mipgap",
        type="float",
        default=None)
parser.add_option("--model-name",
        help="The name of the model object that is created in the specified Pyomo module",
        action="store",
        dest="model_name",
        type="string",
        default="model")
parser.add_option("--model-options",
        help="Options passed into a create_model() function to construct the model",
        action="append",
        dest="model_options",
        type="string",
        default=[])
parser.add_option("--disable-gc",
        help="Disable the garbage collecter",
        action="store_true",
        dest="disable_gc",
        default=False)
parser.add_option("--solver-manager",
        help="Specify the technique that is used to manage solver executions.",
        action="store",
        dest="smanager_type",
        default="serial")
parser.add_option("--stream-output",
        help="Stream the solver output to provide information about the solver's progress.",
        action="store_true",
        dest="tee",
        default=False)
parser.add_option("--save-model",
        help="Specify the filename to which the model is saved.  The suffix of this filename specifies the file format.  If debugging is on, then this defaults to writing the file 'unknown.lp'.",
        action="store",
        dest="save_model",
        default=None)
#
# These options are depricated until we have a specific use-case for them
#
##if False:
##  parser.add_option("--seed",
##        help="Specify a seed to derandomize the solver",
##        action="store",
##        dest="seed",
##        type="int",
##        default=0)
##  parser.add_option("--first-feasible",
##        help="Terminate after the first feasible incumbent",
##        action="store_true",
##        dest="ff",
##        default=False)
parser.usage="pyomo [options] <model.py> [<model.dat>]"


def run_pyomo(options, args):
    #
    # Run the a command that executes a Pyomo script
    #
    if options.help_components:
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
        return

    #
    # Process command-line options
    #
    if options.disable_gc:
        gc.disable()
    if options.verbose:
       pyomo.set_debugging("verbose")
    if options.debug is not None:
       for val in options.debug:
         pyomo.set_debugging( val )
    if not options.logfile is None:
        pyutilib.misc.setup_redirect(options.logfile)
    if not options.tempdir is None:
        if not os.path.exists(options.tempdir):
            raise ValueError, "Directory for temporary files does not exist: "+options.tempdir
        pyutilib.services.TempfileManager.tempdir = options.tempdir

    filter_excepthook=True
    def pyomo_excepthook(etype,value,tb):
      print ""
      if filter_excepthook:
         print "ERROR: Unexpected exception while loading Pyomo model "+args[0]
      else:
         print "ERROR: Unexpected exception while running Pyomo model "+args[0]
      print "  ",value
      print ""
      tb_list = traceback.extract_tb(tb,None)
      i=0
      if not pyomo.debug("all") and filter_excepthook:
         while i < len(tb_list):
           if args[0] in tb_list[i][0]:
              break
           i += 1
      print "Pyomo Traceback (most recent call last):"
      for item in tb_list[i:]:
        print "  File \""+item[0]+"\", line "+str(item[1])+", in "+item[2]
        if item[3] is not None:
           print "    "+item[3]
      sys.exit(1)
    
    sys.excepthook = pyomo_excepthook

    #
    # Apply preprocessing steps
    #
    for file in options.preprocess:
        preprocess = pyutilib.misc.import_file(file)
        
    #
    #
    # Setup solver and model
    #
    #
    if len(args) == 0:
       parser.print_help()
       return
    for file in args:
      if not os.path.exists(file):
         print "File "+file+" does not exist!"
         sys.exit(1)

    #
    # Create Model
    #
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
    if len(args) == 2:
       suffix = (args[1]).split(".")[-1]
       if suffix == "dat":
          instance = model.create(args[1])
       elif suffix == "py":
          userdata = pyutilib.misc.import_file(args[1])
          if "modeldata" not in dir(userdata):
             print ""
             print "pyomo: No 'modeldata' object created in module "+args[1]
             sys.exit(0)
          if userdata.modeldata is None:
             print ""
             raise SystemExit, "Exiting pyomo: 'modeldata' object equals 'None' in module "+args[1]
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
       options.save_model = 'unknown.lp'
       print "Model instance written in file",options.save_model,"to allow debugging"

    if not options.save_model is None:
        instance.write(filename=options.save_model, format=None)
        if not os.path.exists(options.save_model):
            print "ERROR: file "+options.save_model+" has not been created!"

    if options.only_instance:
        return [instance, None]

    #
    # Create Solver and Perform Optimization
    #
    opt = SolverFactory( options.solver )
    if opt is None:
       raise ValueError, "Problem constructing solver `"+str(options.solver)+"'"
    opt.keepFiles=options.keepfiles or options.log
    if options.timelimit == 0:
       options.timelimit=None
    if options.solver_mipgap is not None:
       opt.mipgap = options.solver_mipgap
    solver_mngr = SolverManagerFactory( options.smanager_type )
    if solver_mngr is None:
       raise ValueError, "Problem constructing solver manager `"+str(options.smanager_type)+"'"
    results = solver_mngr.solve(instance, opt=opt, tee=options.tee, timelimit=options.timelimit, options=" ".join(options.solver_options))
    if results == None:
	    raise ValueError, "opt.solve returned None"
    
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

    for file in options.postprocess:
        postprocess = pyutilib.misc.import_file(file)
        if "postprocess" in dir(postprocess):
            postprocess.postprocess(instance,results)
        
    #
    # Return the model instance and optimization results
    #
    return [instance,results]


def run(args=None):
    #
    # Top-level command that executes a Pyomo script.  This 
    # is segregated from run_pyomo to enable Pyomo profiling.
    #

    #
    #
    # Parse command-line options
    #
    #
    try:
       (options, args) = parser.parse_args(args=args)
    except SystemExit:
       # the parser throws a system exit if "-h" is specified - catch
       # it to exit gracefully.
       return

    #
    # Call the main Pyomo runner with profiling
    #
    if options.profile > 0:
        tfile = pyutilib.services.TempfileManager.create_tempfile(suffix=".profile")
        tmp = cProfile.runctx('run_pyomo(options,args)',globals(),locals(),tfile)
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
            ans = run_pyomo(options, args)
        except SystemExit, err:
            if pyomo.debug('errors'):
                sys.exit(0)
            print 'Exiting pyomo:', str(err)
            ans = None
        except Exception, err:
            if pyomo.debug('errors'):
                raise
            print ""
            print "ERROR:",str(err)
            ans = None

    gc.enable()
    return ans

