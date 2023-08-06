var service_descriptions = {commands:{}, responses: {}, events: {}};
% for service in services:
service_descriptions.commands.${service.name} = 
[
  % for command in service.itercommands():
  "${command.name}",
  % endfor
];
% endfor
% for service in services:
service_descriptions.events.${service.name} = 
[
  % for event in service.iterevents():
  "${event.name}",
  % endfor
];
% endfor
