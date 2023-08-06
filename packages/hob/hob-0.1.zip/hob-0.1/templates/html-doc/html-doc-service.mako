<%include file="html-doc-header.mako"/>
% if service.doc:
${service.doc.toComment()}
% endif
<h1>Service ${service.name}</h1>
<%include file="html-doc-status.mako"/>
<h2>Service Definition</h2>
<pre>
service ${service.name}
{
    option version          = ${strquote(service.version)};
    option core_release     = ${strquote(service.coreRelease)};
<% 
  commands = [(
      command.name,
      command.doc,
      command.messageName(),
      command.responseName(),
      command.id,
      len(command.name) + len(command.messageName()),
      len(command.responseName()) ) for command in service.itercommands()]
  events = [(
      event.name,
      event.messageName(),
      event.id,
      len(event.name),
      len(event.messageName()) ) for event in service.iterevents()]
  max_command_length = max(map(lambda x: x[5], commands) + map(lambda x: x[3], events) + [0])
  max_return_length = max(map(lambda x: x[6], commands) + map(lambda x: x[4], events)+ [0])
%>
% for name, doc, messageName, responseName, id, com_length, res_length in commands:
  % if doc:
    % for line in doc.toComment().splitlines():
    ${line}
    % endfor
  % endif
    command ${name}(<a href="#${messageName}" class="message-class">${messageName}</a>) ${' ' * (max_command_length - com_length)}\
returns <a href="#${responseName}" class="message-class">${responseName}</a> ${' ' * (max_return_length - res_length)}= ${id};
% endfor
% for name, messageName, id, com_length, res_length in events:
    event   ${name}   ${' ' * (max_command_length - com_length)}returns <a href="#${messageName}" class="message-class">${messageName}</a> ${' ' * (max_return_length - res_length)}= ${id};
% endfor
}
</pre>
<h2>Messages</h2>

