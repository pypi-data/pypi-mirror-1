syntax = scope;

% if not export or "package" in export:
%   if package.name:
package ${package.name};

%   endif
%   if package.options:
${g.blockOptions(package, package.options)}
%   endif
% endif \

% for item in package.items:
%   if not export or type(item).__name__.lower() in export:
${g.item(item)}

%   endif
% endfor