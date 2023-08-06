<%
  def get_submessages(fields, names=[]):
    ret = []
    for field in fields:
      if field.message and not field.message.name in names:
        names.append(field.message.name)
        ret.append(field)
        ret += get_submessages(field.message.fields, names)
    return ret

  def array_doc(doc):
    if not doc:
      return ""
    return '"' + '", "'.join(doc.replace('\r', '').replace('"', '\\"').split('\n')) + '"';
%>\
<!doctype html>
<html>
<head>
% if create_test_framework:
  <title>Basic test framework of the Opera scope DOM API</title>
  <link rel="stylesheet" href="style.css">
  <script src="${lib_dir}/json.js"></script>
  <script src="${lib_dir}/namespace.js"></script>
  <script src="${lib_dir}/messages.js"></script>
  <script src="${lib_dir}/utils.js"></script>
  <script src="${lib_dir}/clientlib_async.js"></script>
  <script src="${lib_dir}/http_interface.js"></script>
  <script src="${lib_dir}/stp_0_wrapper.js"></script>
  <script src="${lib_dir}/tag_manager.js"></script>
  <script src="${lib_dir}/message_maps.js"></script>
  <script src="logger.js"></script>
  <script src="test_framework.js"></script>
  <script src="${lib_dir}/service_descriptions.js"></script>
  <script src="${lib_dir}/service_base.js"></script>
  <script src="runtimes.js"></script>
  <script src="dom.js"></script>
  <script src="windows.js"></script>
  <script src="client.js"></script>
  <script src="build_application.js"></script>
% elif console_logger_tutorial:
  <title>Simple Console Logger</title>
  <style> pre { border-bottom: 1px solid #999; padding-bottom: 1em; } </style>
  <script src="${lib_dir}/json.js"></script>
  <script src="${lib_dir}/namespace.js"></script>
  <script src="${lib_dir}/messages.js"></script>
  <script src="${lib_dir}/clientlib_async.js"></script>
  <script src="${lib_dir}/http_interface.js"></script>
  <script src="${lib_dir}/stp_0_wrapper.js"></script>
  <script src="${lib_dir}/tag_manager.js"></script>
  <script src="${lib_dir}/service_base.js"></script>
  <script src="client.js"></script>
  <script src="build_application.js"></script>
  <script src="simpleconsolelogger.js"></script>
% else:
  <title> </title>
  <script src="${lib_dir}/json.js"></script>
  <script src="${lib_dir}/namespace.js"></script>
  <script src="${lib_dir}/messages.js"></script>
  <script src="${lib_dir}/clientlib_async.js"></script>
  <script src="${lib_dir}/http_interface.js"></script>
  <script src="${lib_dir}/stp_0_wrapper.js"></script>
  <script src="${lib_dir}/tag_manager.js"></script>
  <script src="${lib_dir}/service_base.js"></script>
  <script src="client.js"></script>
  <script src="build_application.js"></script>
% endif
% for service in services:
  <script src="${lib_dir}/${dashed_name(service.name, dash='_')}_${service.options["version"].value.replace('.', '_')}.js"></script>
% endfor
% for service in services:
  <script src="${lib_dir}/message-maps/message_map_${dashed_name(service.name, dash='_')}_${service.options["version"].value.replace('.', '_')}.js"></script>
% endfor
</head>
<body>
% if create_test_framework:
  <h1><img src="http://www.opera.com/media/images/logo/ologo_wback.gif">Test Framework for STP 1 </h1>
  <div class="row">
    <div id="log">
      <h2>Log</h2>
      <div id="log-container">
        <pre></pre>
      </div>
      <p><input type='button' value='clear log' id='clear-log'><p>
    </div>
    <div id="windows">
      <h2>Window List</h2>
      <ul id="window-list"></ul>
    </div>
  </div>
  <div class="row">
    <div id="services">
      <h2>Service List</h2>
      <ul id="service-list">
  % for service in services:
      <li>${service.name}</li>
  % endfor
      </ul>
    </div>
    <div id="command-list-container">
      <h2>Command List</h2>
      <ul id="command-list"></ul>
    </div>
    <div id="event-list-container">
      <h2>Event List</h2>
      <ul id="event-list"></ul>
    </div>
    <div id="message-container"></div>
  </div>
  <div id="dom-tree">
    <h2>DOM Tree</h2>
    <div id="dom-tree-container" class='dom'></div>
  </div>
% endif
</body>
</html>
