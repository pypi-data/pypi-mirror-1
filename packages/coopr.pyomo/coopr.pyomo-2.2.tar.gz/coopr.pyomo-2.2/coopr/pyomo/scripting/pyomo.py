#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


from optparse import OptionParser
from coopr.pyomo import pyomo
from coopr.opt.base import SolverFactory
from pyutilib.misc import Options, Container

import util

def create_parser():
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
    #
    return parser


def run_pyomo(options=Options(), args=(), parser=None):
    if options.help_components:
        util.print_components(options)
        return Container()
    if not util.setup_environment(options, args):
        return                                               #pragma:nocover
    if not util.apply_preprocessing(options, parser, args):
        return Container()                                   #pragma:nocover
    instance = util.create_model(options, args)
    if options.save_model or options.only_instance:
        return Container(instance=instance)
    results, opt = util.apply_optimizer(options, instance)
    if not util.process_results(options, instance, results, opt):
        return Container(instance=instance, results=results) #pragma:nocover
    util.apply_postprocessing(options, instance, results)
    return Container(instance=instance, results=results)


def run(args=None):
    return util.run_command(run_pyomo, create_parser(), args=args, name='pyomo')

