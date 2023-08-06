<%
  local_comments = comments or ["/** \n", " * ", " */"]
  span_close = classes and "</span>" or ""
  spans = {
      "comment": classes and "<span class=\"comment\">" or "",
      "message": classes and "<span class=\"message\">" or "",
      "number": classes and "<span class=\"number\">" or "",
      "bool": classes and "<span class=\"bool\">" or "",
      "string": classes and "<span class=\"string\">" or "",
      "bytes": classes and "<span class=\"bytes\">" or ""
    } 
  def get_maxs(message):   
    q, type, name, number = [], [], [], []
    for field in message.fields:
      q.append(len(field.q.name))
      type.append(len(field.typename()))
      name.append(len(field.name))
      number.append(len(str(field.number)))
    return {  
        'q': q and max(q) or 0, 
        'type': type and max(type) or 0, 
        'name': name and max(name) or 0, 
        'number': number and max(number) or 0
      }

  def get_submessages(fields, names=[]):
      ret = []
      for field in fields:
          if field.message and not field.message.name in names:
              names.append(field.message.name)
              ret.append(field)
              ret += get_submessages(field.message.fields, names)
      return ret
  submessages = get_submessages(message.fields)
%>\
  ## ************************************************************** ##
  ## def
  ## ************************************************************** ##
  ## print_doc
  ## ************************************************************** ##
<%def name="print_doc(field, indent_level=0, indent='  ')">\
${(local_comments[0] and indent_level or 0)*indent}${spans['comment']}${local_comments[0]}\
      % for line in field.doc.text.splitlines():
${(indent_level)*indent}${local_comments[1]}${line.strip('\r\n')}
      % endfor
${(indent_level)*indent}${local_comments[2]}${span_close}\
</%def>\
  ## message_def
  ## ************************************************************** ##
<%def name="message_def(message, submessages=None, indent_level=0, indent='  ')">\
<% maxs = get_maxs(message) %>\
  % if message.doc:
${print_doc(message, indent_level, indent)}
  % endif
  % if message.comment:
${indent_level*indent}${spans['comment']}// ${message.comment}${span_close}
  % endif
${indent_level*indent}message ${spans['message']}${message.name}${span_close}
${indent_level*indent}{
  % if submessages:
    % for submsg in submessages:
${message_def(submsg.message, submessages=None, indent_level=indent_level+1)}
    % endfor
  % endif
  % for field in message.fields:
    % if field.doc:
${print_doc(field, indent_level+1, indent)}
    % endif
    % if field.comment:
${(indent_level+1)*indent}${spans['comment'] + "// " + field.comment + span_close}
    % endif
${(indent_level+1)*indent}${field.q.name.ljust(maxs['q'])} \
${spans[protoHTMLClass(field)]}${field.typename().ljust(maxs['type'])}${span_close} \
${field.name.ljust(maxs['name'])} = \
${str(field.number).rjust(maxs['number'])}; 
  % endfor
${indent_level*indent}}\
</%def>\
  ## ************************************************************** ##
  ## template
  ## ************************************************************** ##
${message_def(message, submessages=submessages, indent_level=indent_level)}
