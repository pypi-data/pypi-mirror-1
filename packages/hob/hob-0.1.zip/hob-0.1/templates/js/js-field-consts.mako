## message ( command.response or event ), indent, filter
<% 
  def get_fields(name, fields, names=[], all_names=[]):
    ret = [(index, field, ',', field.name in all_names) for index, field in enumerate(fields)]
    names.append(name)
    for field in fields:
      if not field.name in all_names:
        all_names.append(field.name)
    for field in fields:
      if field.message and not field.message.name in names:
        names.append(field.message.name)
        ret.append((0, field.message.name, '/*', False))
        ret += get_fields(field.message.name, field.message.fields, names, all_names)
    if ret:
      last = ret[len(ret) - 1]
      ret[len(ret) - 1] = (last[0], last[1], ';', last[3])
    return ret

  fields = get_fields(message.name, message.fields, [], [])
  fields_count = len(fields)
  sub_msg_name = ""
  command_implemented = False
%>\
## generte all constant identifiers for the message fields
% if fields_count:
${indent}const
  % for index, field, sep, is_name_conflict in fields:
    % if sep == '/*':
<% sub_msg_name = field %>\
${indent}// sub message ${field} 
    % else:
${indent}${is_name_conflict and sub_msg_name.upper() + '_' or ''}${const_id(field, name)} = ${index}${sep}
    % endif
  % endfor
 % endif