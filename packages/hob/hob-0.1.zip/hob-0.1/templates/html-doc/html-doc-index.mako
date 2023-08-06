<%include file="html-doc-header.mako"/>
<h1>STP 1 Service Definitions</h1>
<%include file="html-doc-status.mako"/>
<ul>
% for service in services:
    <li><a href="${service.name}.html">${service.name}</a></li>
% endfor
</ul>
<%include file="html-doc-footer.mako"/>


