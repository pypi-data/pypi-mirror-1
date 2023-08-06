<%
  service_name = dashed_name(service.name)
  commands = [command for command in service.itercommands()]
  events = [event for event in service.iterevents()]
  def is_implemented(service_name, message_name):
    default_implementations = {
        'scope': ['HostInfo', 'Enable'],
        'window-manager': ['ModifyFilter']
      }
    return service_name in default_implementations and \
        message_name in default_implementations[service_name]

  if "version" not in service.options:
      raise Exception("Option 'version' is not set on service %s" % service.name)
  version = service.options["version"].value
%>\
window.cls || (window.cls = {});
cls.${service.name} || (cls.${service.name} = {});
cls.${service.name}["${version}"] || (cls.${service.name}["${version}"] = {});
cls.${service.name}["${version}"].name = '${service_name}';

/**
  * @constructor 
  * @extends ServiceBase
  * generated with hob from the service definitions
  */

cls.${service.name}["${version}"].Service = function()
{
  /**
    * The name of the service used in scope in ScopeTransferProtocol
    */
  this.name = '${service_name}';
  this.version = '${version}';

  ## ************************************************************** ##
  ## commands
  ## ************************************************************** ##
% for command in commands:
<% command_implemented = is_implemented(service_name, command.name) %>\

  // see ${doc_rot_url}${service.name}.html#${command.name.lower()}
  this.request${command.name} = function(tag, message)
  {
    % if service_name == "window-manager":
      % if command.name == "ModifyFilter":
    this._window_filter = message;
      % endif
    % endif
    % if service_name == "scope":
      % if command.name == "Enable":
${generate_field_consts(command.message, lookup, create_test_framework, indent='    ')}\
    ( this._enable_requests || ( this._enable_requests = {} ) )[message[${const_id(command.message.fields[0])}]] = false;
      % endif
    % endif
    opera.scopeTransmit('${service_name}', message || [], ${command.id}, tag || 0);
  }
  this.handle${command.name} = function(status, message)
  {
  ## generte all constant identifiers for the message fields
<% field_consts = generate_field_consts(command.response, lookup, create_test_framework, indent='    ') %>\
    % if field_consts:
      % if not command_implemented:
    /*
      % endif
${field_consts}\
    ${not command_implemented and '*/' or ''}
    % endif
  ##
  ## default command implementations
  ## ************************************************************** ##
  ## scope
  ## ************************************************************** ##
  % if service_name == "scope":
    % if command.name == "HostInfo":
    hello_message = 
    {
      % for field in command.response.fields: 
<% services_message = field.name == "serviceList" and field.message or None %>\
      ${field.name}: message[${const_id(field)}],
      % endfor
    };
    service_descriptions = {};
    var service = null, _services = message[SERVICE_LIST], i = 0, tag = 0;
    for( ; service = _services[i]; i++)
    {
      service_descriptions[service[NAME]] = 
      {
        % if services_message:
        % for field in services_message.fields:
        ${field.name}: service[${const_id(field)}],
        % endfor
        % endif
        index: i
      }
    }
    this._onHostInfoCallback(service_descriptions);
    for( i = 0; service = _services[i]; i++)
    {
      // ensure that the window-manager is the last service to get enabled
      if(service[NAME] in window.services && window.services[service[NAME]].is_implemented &&
        !(service[NAME] == "scope" || service[NAME] == "window-manager") )
      {
        window.services['scope'].requestEnable(0,[service[NAME]]);
      }
    }
    if ("window-manager" in services)
    {
      window.services['scope'].requestEnable(0,["window-manager"]);
    }
    hello_message.services = service_descriptions;    
    % endif
    % if command.name == "Enable":
    var 
    all_enabled = true,
    service = message[${const_id(command.response.fields[0])}],
    service_name = '';

    if(status == 0)
    {
      services[service].post('enable-success');
      services[service].on_enable_success();
      this._enable_requests[service] = true;
      for(service_name in this._enable_requests)
      {
        all_enabled = all_enabled && this._enable_requests[service_name];
      }
      if(all_enabled)
      {
        window.app.post('services-enabled');
        if (window.app.on_services_enabled)
        {
          window.app.on_services_enabled();
        }
        if (this._on_services_enabled_callback)
        {
          this._on_services_enabled_callback();
        }
      }
    }
    else
    {
      opera.postError("enable service failed, message: " + service)
    }
    
    % endif
  ## window-manager
  ## ************************************************************** ##
  % elif service_name == "window-manager":
    % if command.name == "ModifyFilter":
    if(status == 0)
    {
      for( var service in services )
      {
        if(services[service].is_implemented)
        {
          services[service].post('window-filter-change', {filter: this._window_filter});
          services[service].on_window_filter_change(this._window_filter);
        }
      }
    }
    else
    {
      // TODO
    }
    % endif
  % endif
  ## default 
  ## ************************************************************** ##
  % if not command_implemented:
    opera.postError("NotBoundWarning: ${service.name}, ${command.name}");
  % endif
  }
% endfor
  ## end commands
  ## ************************************************************** ##
  ## events
  ## ************************************************************** ##
% for event in events:
  ## sort out implementations

  // see ${doc_rot_url}${service.name}.html#${event.name.lower()}
  this.${event.name.replace('On', 'on')} = function(status, message)
  {
    /*
${generate_field_consts(event.message, lookup, create_test_framework, indent='    ')}\
    */
  ## default
  ## ************************************************************** ##
    opera.postError("NotBoundWarning: ${service.name}, ${event.name}");
  }
% endfor
  ## end events
  ## ************************************************************** ##
  ## basic implemenations
  ## ************************************************************** ##
  % if service_name == "scope":

  var self = this;
  var services_avaible = [];
  var hello_message = {};
  var service_descriptions = {};

  this.get_hello_message = function()
  {
    return hello_message;
  }

  this.set_host_info_callback = function(on_host_info_callback)
  {
    this._onHostInfoCallback = on_host_info_callback;
  }

  this.set_services_enabled_callback = function(on_services_enabled)
  {
    this._on_services_enabled_callback = on_services_enabled;
  }
  % endif
}
