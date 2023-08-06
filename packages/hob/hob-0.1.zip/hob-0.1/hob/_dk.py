from hob.proto import *
from hob.utils import dashed_name, DIST_ROOT, tempdir
from mako.template import Template
from mako.lookup import TemplateLookup
import os
import codecs



def generate_message_defs(message, lookup, indent_level=0):
    return lookup.get_template('py-messages.mako').render_unicode(
        message=message,
        indent_level=indent_level,
        classes=False,
        lookup=lookup
        )

def generate_file(services, lookup, template_name, create_test_framework=False, 
        language_context='py'):
    return lookup.get_template(template_name).render_unicode(
        services=services,
        lookup=lookup,
        dashed_name=dashed_name,
        create_test_framework=create_test_framework,
        generate_message_defs=generate_message_defs,
        language_context=language_context
        )


def generate_dk_maps(target, args, out_dir="dk-maps", js_test_framework=False):
    from hob.proto import ServiceManager, iterProtoFiles
    service_list = []
    lookup = TemplateLookup(
        directories=[
            os.path.join(DIST_ROOT, 'templates'), 
            os.path.join(DIST_ROOT, 'templates', 'js'),
            os.path.join(DIST_ROOT, 'templates', 'py')
            ],
        module_directory=tempdir(["mako", "dk"]),
        default_filters=['decode.utf8']
        )
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    for path in iterProtoFiles(target.selectServiceFiles(args)):
        manager = ServiceManager()
        services = manager.loadServiceFile(path)
        if not services:
            print >>sys.stderr, "No service definitions found in file %s" % path
        for service in manager.services:
            service_list.append(service)

    sources = [
        ('command_map.py', 'py-command-map.mako'),
        ]
    for file_name, template in sources:
        text = generate_file(
                    service_list,
                    lookup,
                    template,
                    create_test_framework=js_test_framework
                    )
        path = os.path.join(out_dir, file_name)
        outfile = open(path, "wb")
        outfile.write(codecs.BOM_UTF8)
        outfile.write(text.encode('utf-8'))
        outfile.close()
        print "Wrote %s" % path
