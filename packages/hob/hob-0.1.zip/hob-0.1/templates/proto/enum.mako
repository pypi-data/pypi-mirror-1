% if enum.doc:
${enum.doc.toComment()}
% endif
enum ${enum.name}
{
${g.blockOptions(enum, enum.options, indent=g.level)}
% for value in enum.values:
  % if value.doc:
${value.doc.toComment(indent=g.level)}
  % endif
${" "*g.line}${value.name} = ${value.value}${g.inlineOptions(value, value.options)};
% endfor
}