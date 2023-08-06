<%
  service_name = dashed_name(service.name)
  commands = [command for command in service.itercommands()]
  events = [event for event in service.iterevents()]
%>\
<%def name="message_def(message)">\
  /**
    * ${"\n    * ".join(generate_proto_defs(
    message, 
    lookup, 
    create_test_framework=create_test_framework, 
    classes=False,
    comments=["", "// ", "//"]).split('\n')).rstrip(" ")}/\
</%def>\
window.cls || (window.cls = {});
cls.${service.name} || (cls.${service.name} = {});
cls.${service.name}["${service.version}"] || (cls.${service.name}["${service.version}"] = {});

/**
  * @constructor 
  * @extends ServiceBase
  * generated with hob from the service definitions
  */

cls.${service.name}["${service.version}"].ServiceInterface = function()
{
  /**
    * The name of the service used in scope in ScopeTransferProtocol
    */
  this.name = '${service_name}';
  this.version = '${service.version}';

% if commands:
  /** 
    * Commands and there according default callback handlers
    * Documentation of message formats see also
    * http://dragonfly.opera.com/app/scope-interface/
    */

% endif
% for command in commands:
${message_def(command.message)}
  this.request${command.name} = function(tag, message){throw "NotImplementedException: request${command.name}"};

${message_def(command.response)}
  this.handle${command.name} = function(status, message){throw "NotImplementedException: handle${command.name}"};

% endfor
% if events:
  /** 
    * Events
    * Documentation of message formats see also
    * http://dragonfly.opera.com/app/scope-interface/
    */

% endif
% for event in events:
${message_def(event.message)}
  this.${event.name.replace('On', 'on')} = function(status, message){throw "NotImplementedException: ${event.name.replace('On', 'on')}"};

% endfor
}

<%doc>
generate_proto_defs(message, lookup, create_test_framework=False)
</%doc>


