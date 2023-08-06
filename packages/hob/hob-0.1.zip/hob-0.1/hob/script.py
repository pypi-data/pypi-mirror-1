"""A multi-language code generator for the Opera Scope Protocol. Code is generated from Google Protocol Buffer definitions.
"""

import sys
import os
from copy import copy

# This imports the argparse module, either globally if the version is sufficient or the bundled version
from distutils.version import StrictVersion
try:
    import argparse
    if not hasattr(argparse, "__version__") or StrictVersion(argparse.__version__) < "1.0":
        del argparse
        from hob.ext import argparse
except ImportError:
    from hob.ext import argparse

from hob.proto import OperaValidator, ValidationError, PackageManager, ErrorType, iterTree, Config, ConfigError, Target, defaultPath
from hob.template import TextGenerator
from hob.cmd import CommandTable, ProgramError
from hob.utils import _
from hob.ui import UserInterface
from hob import extension

__version__ = "0.1"
__author__ = "Jan Borsodi, Christian Krebs"
__author_email__ = "jborsodi@opera.com, chrisk@opera.com"
__program__ = "hob"

__all__ = ("run_exit", "main",
           )

_exts = extension.Manager()
cmds = CommandTable()

warnings = ["all"] + ErrorType.warnings
class WarningAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        for value in values:
            if value not in warnings:
                parser.error("Warning value %r for option %s is not valid, valid warnings are: %s" % (value, option_string, ", ".join(warnings)))
            getattr(namespace, "warning", []).append(value)

global_options = [
    ('', 'verbose', False,
     _('increase verbosity')),
    ('', 'quiet', False,
     _('be silent')),
    ('', 'config_file', '',
     _("use specific config file instead of system-wide/local config files")),
    ('w', 'warning', [],
     _("enable a warning flag, pick from %s" % ", ".join(warnings)),
     WarningAction),
     ]

@cmds.options(global_options)
def main_options(ui, verbose, quiet, config_file, warning, **kwargs):
    if config_file:
        ui.config.reset()
        ui.config.reads("[hob]\ntarget=current\n")
        ui.config.read([config_file])
        ui.config.base = os.path.abspath(os.path.dirname(config_file))

    PackageManager.validator_type = OperaValidator

    for w in warning:
        PackageManager.validator.enableWarning(w)

    if verbose:
        ui.verbose_level += 1
    if quiet:
        ui.verbose_level = 0

@cmds.add()
def extensions(ui, **kwargs):
    """Lists all enabled extensions
    """
    ui.outl("enabled extensions:")
    ui.outl()
    for ext in _exts:
        doc = ext.doc or ""
        doc = doc.splitlines()[0]
        ui.outl(" %s %s" % (ext.name.ljust(12), doc))

@cmds.add([],
    [
    (('service', 'services'), [],
     _("name of the service to validate or a path to a definition file")),
     ])
def validate(ui, services=[], **kwargs):
    """Validates services, commands, events, messages and fields according to the style guide
    """
    from hob.proto import PackageManager
    if not services:
        services = list(ui.config.currentTarget().services())
    for path in services:
        manager = PackageManager(strict=False)
        if not os.path.isfile(path):
            path = ui.config.currentTarget().servicePath(path)
        ui.out("Scanning %s" % path)
        try:
            pkg = manager.loadFile(path, validate=False)
        except IOError, e:
            ui.outl()
            raise ProgramError("Cannot open proto file '%s': %s" % (path, e.strerror))
        if not pkg:
            ui.out("\nNo protocol buffer definitions found in file %s\n" % path)
        else:
            for service in pkg.services:
                validator = PackageManager.validator_type()
                validator.validateService(service, path=path)
                for message in iterTree(service.messages()):
                    validator.validateMessage(message, service=service, path=path)
                if validator.errors or validator.warnings:
                    ui.outl(" Error")
                    for error in validator.errors:
                        ui.warnl(error)
                    for warning in validator.warnings:
                        ui.warnl(warning)
                else:
                    ui.outl(" OK")

@cmds.add([
    ('', 'out_file', None,
     _("write generated code to specified file")),
    ('', 'out_dir', None,
     _("write generated code to specified directory, one file is generated per service")),
    ('t', ('type', 'types'), [],
     _("types to export, default is to export all types. choose from package, service, message and enum")),
     ],
    [
    (('service', 'services'), [],
     _("name of the service to generate definitions for or a path to a definition file")),
     ])
def proto(ui, services, out_file, out_dir, types, **kwargs):
    """Generate Protocol Buffer definitions
    """
    from hob.proto import PackageManager
    f = sys.stdout
    if out_dir:
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
    elif out_file:
        f = open(out_file, "w")
    if not services:
        services = list(ui.config.currentTarget().services())

    if not types:
        types = ["package", "service", "message", "enum"]

    text = ""
    for fname in services:
        try:
            if os.path.isfile(fname):
                manager = PackageManager()
                package = manager.loadFile(fname)
            else:
                package = ui.config.currentTarget().findPackage(fname)
        except IOError, e:
            raise ProgramError("Cannot open proto file '%s': %s" % (fname, e.strerror))

        gen = TextGenerator()
        text = gen.package(package, export=types)
        if out_dir:
            fname = os.path.join(out_dir, service.name + ".txt")
            outfile = open(fname, "w").write(text)
            ui.outl("Wrote service %s to '%s'" % (service.name, fname))
        else:
            f.write(text)

@cmds.add(
    [
    ('', 'out_file', None,
     _("write generated code to specified file")),
    ('', 'out_dir', None,
     _("write generated code to specified directory, one file is generated per service")),
    ('', 'compact', False,
     _("Write compact XML for machine use")),
     ],
    [(('service', 'services'), [],
      _("name of the service to generate definitions for or a path to a definition file")),
    ])
def xml(ui, services, out_file, out_dir, compact, **kwargs):
    """Generate XML structures of protocol definitions
    """
    from hob.proto import PackageManager
    from hob._xmlgen import createDocument, createServiceNode, generateXML
    
    xmlfunc = "toprettyxml"
    if compact:
        xmlfunc = "toxml"

    f = sys.stdout
    if out_dir:
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
    elif out_file:
        f = open(out_file, "w")
    if not services:
        services = list(ui.config.currentTarget().services())
    if not out_dir:
        doc = createDocument()
    for fname in services:
        if out_dir:
            doc = createDocument()
        if os.path.isfile(fname):
            manager = PackageManager()
            package = manager.loadFile(fname)
            if not package:
                print >>sys.stderr, "No protocol buffer definitions found in file %s" % fname
        else:
            package = ui.config.currentTarget().findPackage(fname)
        node = doc.documentElement
        generateXML(package, node)
        if out_dir:
            text = getattr(doc, xmlfunc)()
            fname = os.path.join(out_dir, service.name + ".xml")
            outfile = open(fname, "w").write(text)
            print "Wrote service %s to '%s'" % (service.name, fname)
    if not out_dir:
        text = getattr(doc, xmlfunc)()
        f.write(text)

@cmds.add(
    [('', 'out_dir', "rst-doc",
      _("write generated rst-docs to specified directory, one file is generated per service. Default is 'rst-doc'")),
      ],
    [(('service', 'services'), [],
      _("name of the service to generate code for or a path to a definition file")),
      ])
def rst_doc(ui, services, out_dir, **kwargs):
    """Create reST documentation of selected services.
    If no files are specified all services are added.
    """
    import hob._rst
    hob._rst.generate_rst(ui.config.currentTarget(), services, out_dir)

@cmds.add(
    [('', 'out_dir', "dk-maps",
      _("write generated maps to specified directory, one file is generated for all services. Default is 'dk-maps'.")),
     ('', 'js_test_framework', False,
      _("create a test framework")),
      ],
    [(('service', 'services'), [],
      _("name of the service to generate code for or a path to a definition file")),
      ])
def dk_maps(ui, services, js_test_framework, out_dir, **kwargs):
    """Create maps for dragonkeeper to pretty print messages.
    If no files are specified all services are added.
    """
    import hob._dk
    hob._dk.generate_dk_maps(ui.config.currentTarget(), services, out_dir=out_dir, js_test_framework=js_test_framework)

@cmds.add(
    [('', 'out_dir', 'js-out',
      _("write generated JS files to specified directory, one file is generated per service. Default is 'js-out'.")),
     ('', 'js_test_framework', False,
      _("create a test framework")),
     ('', 'console_logger_tutorial', False,
      _("create the files of the console logger tutorial")),
      ],
    [(('service', 'services'), [],
      _("name of the service to generate code for or a path to a definition file")),
      ])
def js(ui, services, out_dir, js_test_framework, console_logger_tutorial, **kwargs):
    """Create service interfaces for JavaScript.
    If no files are specified, the following files
    will be added in the 'service' folder: 
    console_logger.py, 
    http_logger.py, 
    scope.py, 
    window_manager.py, 
    ecmascript_debugger.py. 
    Files can also be specified with the service name, 
    e.g. just ecmascript-debugger. 
    scope.py and window_manager.py will always be added."""
    import hob._js
    hob._js.generate_services(ui.config.currentTarget(), services, out_dir, js_test_framework, console_logger_tutorial)

def main(args=None):
    try:
        from mako.template import Template
    except ImportError:
        raise ProgramError("Python package `mako` is not installed, without this code-generation is not possible.\nGet it from http://www.makotemplates.org/")

    ui = UserInterface(_exts, cmds)
    ui.config.read(defaultPath)
    ui.config.reads("[hob]\ntarget=current\n")
    _exts.setup(ui, cmds)
    parser = argparse.ArgumentParser(version=__version__, prog=__program__)
    cmds.setup(parser)
    opts = parser.parse_args(args)
    return cmds.process(ui, opts)

def run_exit(args=None):
    try:
        sys.exit(main(args))
    except (ProgramError, ValidationError, ConfigError), e:
        print >>sys.stderr, e
        sys.exit(1)
#    except Exception, e:
#        print >>sys.stderr, "%s: %s" % (type(e).__name__, str(e))
#        sys.exit(1)

if __name__ == "__main__":
    run_exit()
