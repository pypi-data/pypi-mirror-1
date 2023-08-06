Service
=======

% if service.doc:
${service.doc.text}
% endif

.. code-block:: c

${g.proto(doc=False, level=2).service(service, indent=2)}
