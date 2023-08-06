<%def name="blockOptions(command, indent)">\
% if command.options:
 {
${g.blockOptions(command, command.options, indent=indent + g.level)}
${" "*indent}}\
% endif
</%def>\
<%
  commands = list(service.itercommands())
  namelen = 0
  responselen = 0
  numlen = 0
  for command in commands:
    namelen = max(len(command.name) + len(command.messageName()) + 2, namelen)
    responselen = max(len(command.responseName()) + 2, responselen)
    numlen = max(len(str(command.id)), numlen)
  events = list(service.iterevents())
  for event in events:
    namelen = max(len(event.name), namelen)
    responselen = max(len(event.messageName()) + 2, responselen)
    numlen = max(len(str(event.id)), numlen)
%>\
% if service.doc and g.doc:
${service.doc.toComment()}
% endif
service ${service.name}
{
${g.blockOptions(service, service.options, indent=g.level)} \

% for command in service.itercommands():
  % if command.doc and g.doc:
${command.doc.toComment(indent=g.level)}
  % endif
${" "*g.level}command ${("%s(%s)" % (command.name, command.messageName())).ljust(namelen)} returns ${("(%s)" % command.responseName()).ljust(responselen)} = ${str(command.id).rjust(numlen)}${blockOptions(command, g.level)};
% endfor \

% for event in service.iterevents():
  % if event.doc and g.doc:
${event.doc.toComment(indent=g.level)}
  % endif
${" "*g.level}event   ${event.name.ljust(namelen)} returns ${("(%s)" % event.messageName()).ljust(responselen)} = ${str(event.id).rjust(numlen)}${blockOptions(event, g.level)};
% endfor
}