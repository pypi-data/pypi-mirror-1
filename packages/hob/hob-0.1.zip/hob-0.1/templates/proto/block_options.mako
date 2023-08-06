<%
  opts = list(options.iteritems())
  olen = 0
  for option, value in opts:
    l = len(option)
    if owner.isCustomOption(option):
      l += 2
    olen = max(l, olen)
%>\
% for option, value in opts:
  % if value.doc:
${value.doc.toComment()}
  % endif
  % if owner.isCustomOption(option):
option ${("(%s)" % option).ljust(olen)} = ${value.dumps()};
  % else:
option ${option.ljust(olen)} = ${value.dumps()};
  % endif
% endfor