<% 
  INDENT = "    " 
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
${(indent_level) * "    "}],
</%def>\
${SINGLE_COMMENT_TOKEN} created with hob 

status_map = {
    0: "OK",
    1: "Conflict",
    2: "Unsupported Type",
    3: "Bad Request",
    4: "Internal Error",
    5: "Command Not Found",
    6: "Service Not Found",
    7: "Out Of Memory",
    8: "Service Not Enabled",
    9: "Service Already Enabled",
    }

format_type_map = {
    0: "protocol-buffer",
    1: "json",
    2: "xml"
    }

message_type_map = {
    1: "command", 
    2: "response", 
    3: "event", 
    4: "error"
    }

## This structure should not be hardcoded but generated from a .proto file
package_map = {
  "com.opera.stp": {
    "Error":
    [
            {
                "name": "description",
                "q": "optional",
            },
            {
                "name": "line",
                "q": "optional",
            },
            {
                "name": "column",
                "q": "optional",
            },
            {
                "name": "offset",
                "q": "optional",
            },
        ],

  },
}

window.message_maps || (window.message_maps = {});
