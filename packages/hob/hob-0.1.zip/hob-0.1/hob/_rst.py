from hob.proto import *
from hob.template import Generator, TextGenerator
import os
import codecs
import textwrap
from hob._js import protoHTMLClass

class RstGenerator(Generator):
    def __init_(self, **kwargs):
        super(RstGenerator, self).__init__(lookup_args=dict(default_filters = ['decode.utf8']),
                                           **kwargs)

    def proto(self, **kwargs):
        return TextGenerator(**kwargs)

    def package(self, package, indent=0):
        return self.generate('rst-doc/package.mako', indent,
                             dict(package=package))

    def service(self, service, indent=0):
        return self.generate('rst-doc/rst-doc-service.mako', indent,
                             dict(service=service))

    def commands(self, service, indent=0):
        return self.generate('rst-doc/rst-proto-defs.mako', indent,
                             dict(service=service))

    def message(self, message, indent=0):
        return self.generate('js/js-message-definition.mako', indent,
                              dict(message=message,
                                   indent_level=1,
                                   protoHTMLClass=protoHTMLClass))

def generate_rst(target, services, out_dir="rst-doc"):
    from hob.proto import PackageManager, iterProtoFiles
    rst_doc_service_index = []
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    if not services:
        services = list(target.services())
    for path in services:
        manager = PackageManager()
        if os.path.isfile(path):
            package = manager.loadFile(path)
        else:
            package = target.findPackage(path)
        if not package:
            print >>sys.stderr, "No protocol buffer definitions found in file %s" % path
        for service in package.services:
            rst_doc_service_index.append(service)
        gen = RstGenerator()
        text = gen.package(package)
        fname = os.path.join(out_dir, service.name + ".rst")
        outfile = open(fname, "w").write(text.encode('utf-8'))
        print "Wrote service %s to '%s'" % (service.name, fname)
