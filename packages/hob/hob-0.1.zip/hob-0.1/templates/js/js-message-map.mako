<% 
  INDENT = indent or "  " 
  SINGLE_COMMENT_TOKEN = language_context and language_context == "js" and "//" or "#"

%>\
<%def name="print_fields(message, indent_level=0)">\
[
% for field in message.fields:
${(indent_level + 1 ) * INDENT}{
${(indent_level + 2 ) * INDENT}"name": "${field.name}",
${(indent_level + 2 ) * INDENT}"q": "${field.q.name}",
  % if field.message:
    % if field.message.name == message.name:
${(indent_level + 2 ) * INDENT}"message": "self" 
    % else:
${(indent_level + 2 ) * INDENT}"message": ${print_fields(field.message, indent_level=indent_level + 2)}
    % endif
  % endif
${(indent_level + 1 ) * INDENT}},
% endfor
${(indent_level) * INDENT}],\
</%def>\
${SINGLE_COMMENT_TOKEN} created with hob 

window.message_maps || (window.message_maps = {});
window.message_maps["${dashed_name(service.name)}"] || (window.message_maps["${dashed_name(service.name)}"] = {});

window.message_maps["${dashed_name(service.name)}"]["${service.options["version"].value}"] = {
% for command in service.itercommands():
  ${command.id}: {
    "name": "${command.name}",
    ${SINGLE_COMMENT_TOKEN} command message
    1: ${print_fields(command.message, indent_level=2)}
    ${SINGLE_COMMENT_TOKEN} response message
    2: ${print_fields(command.response, indent_level=2)}
  },
% endfor
% for event in service.iterevents():
  ${event.id}: {
    "name": "${event.name}",
    ${SINGLE_COMMENT_TOKEN} event message
    3: ${print_fields(event.message, indent_level=2)}
  },
% endfor
}
