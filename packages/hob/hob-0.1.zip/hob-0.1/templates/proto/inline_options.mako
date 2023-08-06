% if options:
 [\
% for i, (option, value) in enumerate(options.iteritems()):
  % if value.doc:
${value.doc.toComment(False)} \
  % endif
% if i > 0:
, \
% endif
  % if owner.isCustomOption(option):
(${option}) = ${value.dumps()}\
  % else:
${option} = ${value.dumps()}\
  % endif
% endfor
]\
%endif