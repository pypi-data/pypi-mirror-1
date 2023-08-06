<%
def const_id(field, name=""): 
  return dashed_name(field.message and name or field.name, '_').upper()

def extract_msg(name, fields, msg_list, name_list):
  if name not in name_list:
    msg_list.append((name, fields))
    name_list.append(name)
    for field in fields:
      if field.message:
        extract_msg(field.message.name, field.message.fields, msg_list, name_list)
%>\
% for service in services: 
<%
    msg_names = ['Default']
    msgs = []
    for command in service.itercommands():
        extract_msg(command.messageName(), command.message.fields, msgs, msg_names)
        extract_msg(command.responseName(), command.response.fields, msgs, msg_names)
    for command in service.iterevents():
        extract_msg(command.messageName(), command.message.fields, msgs, msg_names)
%>\

/* ${service.name} */

  % for name, fields in msgs:
  /* ${name} */
    % for index, field in enumerate(fields):
  ${const_id(field, name)} = ${index}, 
    % endfor
  % endfor
% endfor


<%doc>
<%
def const_id(field): 
  if field.message:
    print dir(field.message.fields)
  return dashed_name(field.message and field.message.name or field.name, '_').upper()
%>\
% for service in services: 
<% message_names = ['Default'] %>\

/* ${service.name} */

    % for command in service.itercommands():
        % if not command.messageName() in message_names:
    /* ${command.messageName()} */
          % for index, field in enumerate(command.message.fields):
    ${const_id(field)} = ${index}, 
          % endfor
        % endif
        % if not command.responseName() in message_names:
    /* ${command.responseName()} */
          % for index, field in enumerate(command.response.fields):
    ${const_id(field)} = ${index}, 
          % endfor
        % endif
<% 
  message_names.append(command.messageName())
  message_names.append(command.responseName())
%>\
    % endfor
    % for command in service.iterevents():
        % if not command.messageName() in message_names:
    /* ${command.messageName()} */
          % for index, field in enumerate(command.message.fields):
    ${const_id(field)} = ${index},
          % endfor
        % endif
<% 
  message_names.append(command.messageName())
%>\
    % endfor
% endfor
</%doc>




