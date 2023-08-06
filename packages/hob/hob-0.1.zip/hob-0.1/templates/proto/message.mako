<%
  # TODO: Default value must work when options are present, maybe put default as an option?
  def formatDefault(field):
    if field.default == None:
      return ""
    return " [default = %s]" % field.defaultValue()
  spaces = " "*g.level
%>\
% if message.doc:
${message.doc.toComment()}
% endif
message ${message.name}
{
${g.blockOptions(message, message.options, indent=g.level)}\
\
% if message.extensions:
%   for start, end in message.extensions:
%     if end >= 536870911:
${spaces}extensions ${start} to max;
%     else:
${spaces}extensions ${start} to ${end};
%     endif
%   endfor
% endif \

% if message.children:
% for item in message.items:
${g.item(item, indent=g.level)}

% endfor
% endif \

<%
  fields = []
  lengths = [0]*4
  for field in message.fields:
    columns = [field.doc, field.q.name, field.typename(), field.name, str(field.number), formatDefault(field), g.inlineOptions(field, field.options)]
    for i in range(4):
      lengths[i] = max(lengths[i], len(columns[i + 1]))
    fields.append(columns)
%>\
% for doc, quantifier, kind, name, number, default, options in fields:
  % if doc:
${doc.toComment(indent=g.level)}
  % endif
${spaces}${quantifier.ljust(lengths[0])} ${kind.ljust(lengths[1])} ${name.ljust(lengths[2])} = ${number.rjust(lengths[3])}${default}${options};
% endfor
}