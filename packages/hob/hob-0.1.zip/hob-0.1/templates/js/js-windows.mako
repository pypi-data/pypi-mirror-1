% for service in services:
  % if service.name == "WindowManager" and create_test_framework:
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

cls.${service.name}["${version}"].Windows = function()
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
      % if command.name in ["ListWindows", "GetActiveWindow"]:
  this.handle${command.name} = function(status, message){};
      % endif
    % endfor
  ## ************************************************************** ##
  ## events
  ## ************************************************************** ##
    % for event in events:
      % if event.name in ["OnWindowActivated", "OnWindowUpdated", "OnWindowClosed"]: 
  this.${event.name.replace('On', 'on')} = function(status, message){};
      % endif
    % endfor
  /**
    * to set a new debug context
    * @param {String} window_id the id of the window to be debugged
    */
  this.set_debug_context = function(window_id){};
  /**
    * to update the displayed information about the debug context
    */
  this.update_windows_debug_context = function(){};

  // privat

  this._window_list = [];
  this._debug_context = 0;
  this._actice_window = 0;

  this._update_window_list = function(window)
  {
    const WINDOW_ID = 0;
    for( var win = null, i = 0; ( win = this._window_list[i] ) && 
                                  ( win[WINDOW_ID] != window[WINDOW_ID] ); i++);
    this._window_list[i] = window;
  }

  this._update_view = function()
  {
    document.getElementById("window-list").innerHTML = 
      this._window_list.map(this._template_window, this).join('');
    this.update_windows_debug_context();
  }

  this._template_window = function(win)
  {
    const
    WINDOW_ID = 0, 
    TITLE = 1, 
    WINDOW_TYPE = 2, 
    OPENER_ID = 3;

    var _class = win[WINDOW_ID] == this._debug_context && " class=\"selected\"" || "";

    return (
    "<li" + _class + " data-window-id='" + win[WINDOW_ID] + "'>" +
        win[TITLE] + "<span> [" + win[WINDOW_ID] + "]</span>" +
    "</li>");
  }

  this._remove_window = function(id)
  {
    const
    WINDOW_ID = 0;

    for( var win = null, i = 0; 
        ( win = this._window_list[i] ) && ( win[WINDOW_ID] != id ); 
        i++);
    if(win)
    {
      // TODO check if window is debug_context
      this._window_list.splice(i, 1);
      if( win[WINDOW_ID] == this._debug_context )
      {
        this.set_debug_context(win[WINDOW_ID]);
      }
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
      % if command.name in ["ListWindows", "GetActiveWindow"]:
  this.handle${command.name} = function(status, message)
  {
  ## generte all constant identifiers for the message fields
${generate_field_consts(command.response, lookup, create_test_framework, indent='    ')}\
        % if command.name == "ListWindows":
    message[WINDOW_LIST].map(this._update_window_list, this);
    this._update_view();    
    if( !this._active_window )
    {
      services["${service_name}"].requestGetActiveWindow();
    }
        % elif command.name == "GetActiveWindow":
    if( !this._debug_context )
    {
      this.set_debug_context(message[WINDOW_ID]);
      this._update_view();
    }
        % endif
  }

      % endif
    % endfor
  ## ************************************************************** ##
  ## events
  ## ************************************************************** ##
    % for event in events:
      % if event.name in ["OnWindowActivated", "OnWindowUpdated", "OnWindowClosed"]: 
  this.${event.name.replace('On', 'on')} = function(status, message)
  {
  ## generte all constant identifiers for the message fields
${generate_field_consts(event.message, lookup, create_test_framework, indent='    ')}\
        % if event.name == "OnWindowActivated":
    this._actice_window = message[WINDOW_ID];
    this._update_view(); 
        % elif event.name == "OnWindowUpdated":
    this._update_window_list(message);
    this._actice_window = message[WINDOW_ID];
    this._update_view();
        % elif event.name == "OnWindowClosed":
    this._remove_window(message[WINDOW_ID]);
    this._update_view();
        % endif
  }
      % endif
    % endfor

  this.set_debug_context = function(id)
  {
    const WINDOW_ID = 0;
    for( var win = null, i = 0; 
        ( win = this._window_list[i] ) && ( win[WINDOW_ID] != id ); 
        i++);
    if(win)
    {
      this._debug_context = id;
      if( !this._actice_window )
      {
        this._actice_window = id;
      }
    }
    else if(this._window_list.length)
    {
      this._debug_context = this._window_list[0][WINDOW_ID];
      logger.log_error("window id", id, "does not exist, first window in the list set as debug context instead");
    }
    if(this._debug_context)
    {
      this._window_filter = [1, [this._debug_context]];
      services['window-manager'].requestModifyFilter(0, this._window_filter)
    }
  }

  this.update_windows_debug_context = function()
  {
    const
    /* RuntimeInfo */
    RUNTIME_ID = 0, 
    HTML_FRAME_PATH = 1, 
    WINDOW_ID = 2, 
    OBJECT_ID = 3, 
    URI = 4;

    var 
    runtime_list = runtimes.get_runtime_list() || [],
    i = 0, 
    runtime = null, 
    cur = null;

    while( cur = document.getElementById('windows').getElementsByTagName('pre')[0] )
    {
      cur.parentNode.removeChild(cur);
    }
    for( ; runtime = runtime_list[i]; i++)
    {
      if( cur = document.getElementById('window-id-' + runtime[WINDOW_ID]) )
      {
        cur = cur.appendChild(document.createElement('pre'));
        cur.className = 'runtime-info';
        cur.textContent = runtime[HTML_FRAME_PATH] + ", " + 
          "runtime id: " + runtime[RUNTIME_ID] + ", " +
          "window id: " + runtime[WINDOW_ID];
      }
    }
  }

  var self = this;

  this.bind = function()
  {
    var window_manager = window.services['window-manager'];

    [
      'handleGetActiveWindow', 
      'handleListWindows', 
      'onWindowUpdated',
      'onWindowClosed', 
      'onWindowActivated'
    ].forEach(function(method_name){
      window_manager[method_name] = function(status, message)
      {
        self[method_name](status, message);
      }
    });

    window_manager.on_enable_success = function()
    {
      window_manager.requestListWindows();
    }
    
  }

  this.bind();

}
  % endif
% endfor
