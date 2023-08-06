from hob.proto import *
from hob.utils import dashed_name, DIST_ROOT, tempdir
from hob.cmd import ProgramError
from mako.template import Template
from mako.lookup import TemplateLookup
import os
import codecs

LIB_DIR = "lib"
DOC_ROOT_URL = "http://dragonfly.opera.com/app/scope-interface/"

def protoHTMLClass(field):
    ptypes = {Proto.Message: "message",
              Proto.Int32: "number"
             ,Proto.Uint32: "number"
             ,Proto.Sint32: "number"
             ,Proto.Fixed32: "number"
             ,Proto.Sfixed32: "number"
             ,Proto.Int64: "number"
             ,Proto.Uint64: "number"
             ,Proto.Sint64: "number"
             ,Proto.Fixed64: "number"
             ,Proto.Sfixed64: "number"
             ,Proto.Bool: "bool"
             ,Proto.String: "string"
             ,Proto.Bytes: "bytes"
             ,Proto.Float: "number"
             ,Proto.Double: "number"
             }
    return ptypes[field.type]

class TemplateEnv(object):
    def __init__(self, lookup, out_dir, js_test_framework, console_logger_tutorial):
        self.lookup = lookup
        self.out_dir = out_dir
        self.js_test_framework = js_test_framework
        self.console_logger_tutorial = console_logger_tutorial

def const_id(field, name=""): 
    return dashed_name(field.message and name or field.name, '_').upper()

def generate_service_interface(service, lookup, out_dir, js_test_framework, console_logger_tutorial):
    fname = os.path.join(out_dir, LIB_DIR, 
                    "interface_" + dashed_name(service.name, dash="_") + ".js")
    outfile = open(fname, "wb")
    outfile.write(codecs.BOM_UTF8)
    outfile.write(lookup.get_template('js-service-interface.mako').render_unicode(
        service=service, 
        dashed_name=dashed_name,
        create_test_framework=js_test_framework,
        lookup=lookup,
        generate_proto_defs=generate_proto_defs
        ).encode('utf-8'))
    outfile.close()
    print "Wrote service-interface %s to '%s'" % (service.name, fname)

def generate_service_implementation(service, template_env):
    version = service.options["version"].value.replace('.', '_')
    service_name = dashed_name(service.name, dash="_")
    fname = "%s_%s.js" % (service_name, version)
    fpath = os.path.join(template_env.out_dir,LIB_DIR,fname)
    template = template_env.lookup.get_template("js-service-implementation.mako")
    outfile = open(fpath, "wb")
    outfile.write(codecs.BOM_UTF8)
    outfile.write(template.render_unicode(
        service=service, 
        dashed_name=dashed_name,
        create_test_framework=template_env.js_test_framework,
        lookup=template_env.lookup,
        generate_field_consts=generate_field_consts,
        const_id=const_id,
        console_logger_tutorial=template_env.console_logger_tutorial,
        doc_rot_url=DOC_ROOT_URL
        ).encode('utf-8'))
    outfile.close()
    print "Wrote service-implementation %s to '%s'" % (service.name, fname)
    
def generate_message_map(service, template_env):
    version = service.options["version"].value.replace('.', '_')
    service_name = dashed_name(service.name, dash="_")
    fname = "message_map_%s_%s.js" % (service_name, version)
    fpath = os.path.join(template_env.out_dir, LIB_DIR, "message-maps", fname)
    template = template_env.lookup.get_template("js-message-map.mako")
    outfile = open(fpath, "wb")
    outfile.write(codecs.BOM_UTF8)
    outfile.write(template.render_unicode(
        service=service, 
        dashed_name=dashed_name,
        create_test_framework=template_env.js_test_framework,
        lookup=template_env.lookup,
        generate_field_consts=generate_field_consts,
        const_id=const_id,
        console_logger_tutorial=template_env.console_logger_tutorial,
        doc_rot_url=DOC_ROOT_URL,
        language_context="js"
        ).encode('utf-8'))
    outfile.close()
    print "Wrote message map %s to '%s'" % (service.name, fname)

def generate_file(services, lookup, template_name, create_test_framework=False, 
            console_logger_tutorial=False, lib_dir="", language_context='js'):
    return lookup.get_template(template_name).render_unicode(
        services=services, 
        dashed_name=dashed_name,
        create_test_framework=create_test_framework,
        console_logger_tutorial=console_logger_tutorial,
        lookup=lookup,
        generate_field_consts=generate_field_consts,
        const_id=const_id,
        lib_dir=lib_dir,
        language_context=language_context
        )

def generate_proto_defs(
        message, 
        lookup, 
        create_test_framework=False,
        classes=True, 
        indent_level=0,
        comments=["/** \n", " * ", " */"]
        ):
    return lookup.get_template('js-message-definition.mako').render_unicode(
        message=message,
        protoHTMLClass=protoHTMLClass,
        classes=classes,
        indent_level=indent_level,
        comments=comments
        )

def generate_field_consts(
        message, 
        lookup, 
        create_test_framework=False,
        indent='  '
        ):
    return lookup.get_template('js-field-consts.mako').render_unicode(
        message=message, 
        create_test_framework=create_test_framework,
        dashed_name=dashed_name,
        indent=indent,
        const_id=const_id
        )

def generate_services(target, args, out_dir="js-out", js_test_framework=False, console_logger_tutorial=False):
    from hob.proto import ServiceManager, iterProtoFiles
    import shutil
    lookup = TemplateLookup(
        directories=[
            os.path.join(DIST_ROOT, 'templates'), 
            os.path.join(DIST_ROOT, 'templates', 'js'),
            os.path.join(DIST_ROOT, 'templates', 'py')
            ], 
        module_directory=tempdir(["mako", "js"]),
        default_filters=['decode.utf8']
        )
    service_list = []
    tasks =  [
        generate_service_implementation,
        generate_message_map
    ]
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    if not os.path.exists(os.path.join(out_dir, LIB_DIR)):
        os.makedirs(os.path.join(out_dir, LIB_DIR))
    if not os.path.exists(os.path.join(out_dir, LIB_DIR, "message-maps")):
        os.makedirs(os.path.join(out_dir, LIB_DIR, "message-maps"))
    template_env = TemplateEnv(lookup, out_dir, js_test_framework, console_logger_tutorial)
        
    for path in iterProtoFiles(target.selectServiceFiles(args)):
        manager = PackageManager()
        package = manager.loadFile(path)
        if not package:
            print >>sys.stderr, "No protocol buffer definitions found in file %s" % path
        
        for service in package.services: # TODO: Should generate for package instead?
            if "version" not in service.options:
                raise Exception("Option 'version' is not set on service %s" % service.name)
            service_list.append(service)
            for task in tasks:
                task(service, template_env)
    dependencies = {"Scope": False,
                    "WindowManager": False}
    for service in service_list:
        if service.name in ("Scope", "WindowManager"):
            dependencies[service.name] = True
    if not all(dependencies.itervalues()):
        required = [k for k, v in dependencies.iteritems() if not v]
        raise ProgramError("The following services must be included for the generated code to work: %s" % ", ".join(required))
    sources = [
        ('client.js', 'js-client.mako', ''),
        ('client.html', 'js-client-html.mako', ''),
        ('service_base.js','js-service-base.mako', LIB_DIR),
        ('http_interface.js', 'js-http-interface.mako', LIB_DIR),
        ('stp_0_wrapper.js', 'js-stp-0-wrapper.mako', LIB_DIR),
        ('build_application.js', 'js-build_application.mako', ''),
        ('message_maps.js', 'py-command-map.mako', LIB_DIR),
        ('service_descriptions.js', 'js-service-description.mako', LIB_DIR),
        ]
    if js_test_framework:
        sources += [
            ('runtimes.js', 'js-runtimes.mako', ''),
            ('dom.js', 'js-DOM.mako', ''),
            ('windows.js', 'js-windows.mako', '')
            ]
        
    for file_name, template, rep in sources:
        text = generate_file(
                    service_list, 
                    lookup, 
                    template, 
                    create_test_framework=js_test_framework,
                    console_logger_tutorial=console_logger_tutorial,
                    lib_dir=LIB_DIR,
                    language_context='js'
                    )
        path = os.path.join(out_dir, rep, file_name)
        outfile = open(path, "wb")
        outfile.write(codecs.BOM_UTF8)
        outfile.write(text.encode('utf-8'))
        outfile.close()
        print "Wrote %s" % path

    if js_test_framework:
        def_path = os.path.join(out_dir, 'defs')
        if not os.path.exists(def_path):
            os.mkdir(def_path)
        message_defs = []
        for service in service_list:
            for command in service.itercommands():
                message_defs.append(
                    ("%s.%s.%s.def" % (service.name, 'commands', command.name),
                    generate_proto_defs(command.message, 
                            lookup, create_test_framework=js_test_framework))
                  )
                message_defs.append(
                    ("%s.%s.%s.def" % (service.name, 'responses', command.name),
                    generate_proto_defs(command.response, 
                            lookup, create_test_framework=js_test_framework))
                  )
            for event in service.iterevents():
                message_defs.append(
                    ("%s.%s.%s.def" % (service.name, 'events', event.name),
                    generate_proto_defs(event.message, 
                            lookup, create_test_framework=js_test_framework))
                  )
        for file_name, text in message_defs:
            file = open(os.path.join(out_dir, 'defs', file_name), 'wb')
            file.write(text)
            file.close()
    sources = [
        ('clientlib_async.js', LIB_DIR),
        ('tag_manager.js', LIB_DIR),
        ('json.js', LIB_DIR),
        ('namespace.js', LIB_DIR),
        ('messages.js', LIB_DIR),
        ]
    if js_test_framework:
        sources += [
            ('style.css', ''),
            ('test_framework.js', ''),
            ('logger.js', ''),
            ('utils.js', LIB_DIR)
            ]
    if console_logger_tutorial:
        sources += [
            ('simpleconsolelogger.js', ''),
            ]
    for file_name, repo in sources:
        source_path = os.path.join(DIST_ROOT, 'templates', 'js', file_name)
        shutil.copy(source_path, os.path.join(out_dir, repo))
        print "Copied %s" % source_path
