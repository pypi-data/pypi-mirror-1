<%
  def formatDefault(field):
    if field.default == None:
      return ""
    return " [default = %s]" % field.defaultValue()
  def formatComment(field):
    if not field.comment:
      return ""
    return " // " + field.comment.replace("\n", " ")
  def formatDoc(field):
    if not field.doc:
      return ""
    return field.doc.toComment() 
  TYPE_MAP = {
    'uint32': 'int',
    'string': 'string',
    'bool': 'bool'
    }
    
%>\
<pre id="${message.name}">
% if message.doc:
<span class="comment">${message.doc.toComment()}</span>
% endif
message <span class="message-class">${message.name}</span>
{
% if submessages:
  % for submessage in submessages:
	  % for line in submessage.splitlines(False):
    ${line}
	  % endfor 
  % endfor 
% endif
<%
  fields = []
  lengths = [0]*7
  for field in message.fields:
    columns = [formatDoc(field), field.q.name, field.typename(), field.name, 
                  str(field.number), formatDefault(field), formatComment(field)]
    for i in range(4):
      lengths[i] = max(lengths[i], len(columns[i + 1]))
    fields.append(columns)
%>\
% for doc, quantifier, kind, name, number, default, comment in fields:
  % if doc:
    <span class="comment">
    % for line in doc.splitlines():
    ${line}
    % endfor
    </span>
  % endif
  % if kind in TYPE_MAP: 
    ${quantifier.ljust(lengths[0])} \
<span class="${TYPE_MAP[kind]}">${kind.ljust(lengths[1])}</span> \
${name.ljust(lengths[2])} = \
${number.rjust(lengths[3])}${default};<span class="comment">${comment}</span>
  % else:
    ${quantifier.ljust(lengths[0])} \
<a href="#${kind}" class="message-class">${kind.ljust(lengths[1])}</a> \
${name.ljust(lengths[2])} = \
${number.rjust(lengths[3])}${default};<span class="comment">${comment}</span>
  % endif
% endfor
}
</pre>
