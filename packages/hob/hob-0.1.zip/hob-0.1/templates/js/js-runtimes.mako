% for service in services:
  % if service.name == "EcmascriptDebugger" and create_test_framework:
<%
  service_name = dashed_name(service.name)
  commands = [command for command in service.itercommands()]
  events = [event for event in service.iterevents()]
  if "version" not in service.options:
      raise Exception("Option 'version' is not set on service %s" % service.name)
  version = service.options["version"].value
%>\
window.cls || (window.cls = {});
cls.${service.name} || (cls.${service.name} = {});
cls.${service.name}["${version}"] || (cls.${service.name}["${version}"] = {});

/**
  * @constructor 
  */

cls.${service.name}["${version}"].Runtimes = function()
{
  ## ************************************************************** ##
  ## interface
  ## ************************************************************** ##
  /* interface */

  /* scope interfaces */
  ## ************************************************************** ##
  ## commands
  ## ************************************************************** ##
    % for command in commands:
      % if command.name in ["ListRuntimes"]:
  this.handle${command.name} = function(status, message){};
      % endif
    % endfor
  /**
    * @return the list of the runtimes of the debug context 
    */
  this.get_runtime_list = function(){};

  // privat

  var self = this;

  this._check_top_runtime_loaded = function(status, message)
  {
    const VALUE = 2;

    if( message && message[VALUE] == "complete" )
    {
      window.dom.on_top_runtime_loaded(self._top_runtime_id);
    }
    else
    {
      setTimeout( function(){
        var tag = tagManager.set_callback(self, self._check_top_runtime_loaded);
        var script = "return document.readyState";
        services["${service_name}"].requestEval(tag, [self._top_runtime_id, 0, 0, script]);
      }, 100);
    }
  }

  ## ************************************************************** ##
  ## implementation
  ## ************************************************************** ##
  // implementation
  ## ************************************************************** ##
  ## commands
  ## ************************************************************** ##
    % for command in commands:
      % if command.name in ["ListRuntimes"]:
  this.handle${command.name} = function(status, message)
  {
  ## generate all constant identifiers for the message fields
${generate_field_consts(command.response, lookup, create_test_framework, indent='    ')}\
        % if command.name == "ListRuntimes":
    var runtime_list = message[RUNTIME_LIST], runtime = null, i = 0;
    if(runtime_list)
    {
      for( ; ( runtime = runtime_list[i] ) && ( runtime[HTML_FRAME_PATH] != "_top" ); i++);
      if( runtime )
      {
        this._top_runtime_id = runtime[RUNTIME_ID];
        this._check_top_runtime_loaded();
      }
      this._runtime_list = runtime_list;
      windows.update_windows_debug_context();
    }
    else
    {
      // TODO
    }
        % endif
  }

      % endif
    % endfor
  this.get_runtime_list = function()
  {
    return this._runtime_list;
  }

  this.bind = function()
  {
    var ecmascript_debugger = window.services['ecmascript-debugger'];
    ecmascript_debugger.handleListRuntimes = function(status, message)
    {
      self.handleListRuntimes(status, message);
    }
    ecmascript_debugger.on_enable_success = function()
    {
      this.requestSetConfiguration(0, [0,0,0,0,0,0]);
    }
    ecmascript_debugger.onRuntimeStarted =
    ecmascript_debugger.on_window_filter_change = function()
    {
      this.requestListRuntimes(0, [[], 1]);
    }

  }

  this.bind();

}
  % endif
% endfor
