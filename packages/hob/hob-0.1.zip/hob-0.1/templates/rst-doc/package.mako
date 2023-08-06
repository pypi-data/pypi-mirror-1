<%
    service = package.services[0]
%>\
${len(service.name) * "="}
${service.name}
${len(service.name) * "="}

:Generated:  hob rst-doc
:Version:    ${service.options["version"].value}
:Status:     Draft

${g.service(service)}

${g.commands(service)}
