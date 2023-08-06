var SimpleLogger = function()
{
 
  var _get_or_create_container = function(window_id)
  {
    var container = document.getElementById('window-id-' + window_id);
    if (!container)
    {
      container = document.body.appendChild(document.createElement('div'));
      container.id = 'window-id-' + window_id;
    }
    return container;
  }
 
  var _display_window_title = function(win)
  {
    const WINDOW_ID = 0, TITLE = 1;
    _get_or_create_container(win[WINDOW_ID]).
      appendChild(document.createElement('h2')).textContent = win[TITLE];
  }
 
  // service API bindings

  window.services['window-manager'].handleListWindows = function(status, message)
  {
    const WINDOW_LIST = 0;
    message[WINDOW_LIST].forEach(_display_window_title);
  }

  window.services['window-manager'].onWindowUpdated = function(status, message)
  {
    _display_window_title(message);
  }

  window.services['console-logger'].onConsoleMessage = function(status, message)
  {
    const
    WINDOW_ID = 0,
    TIME = 1,
    DESCRIPTION = 2,
    URI = 3,
    CONTEXT = 4,
    SOURCE = 5,
    SEVERITY = 6;

    var pre = _get_or_create_container(message[WINDOW_ID]).appendChild(document.createElement('pre'));
    pre.textContent = new Date(message[TIME]) + '\n' +
      "source: " + message[SOURCE] + '\n' +
      "uri: " + message[URI] + '\n' +
      "context: " + message[CONTEXT] + '\n' +
      "severity: " + message[SEVERITY] + '\n' +
      message[DESCRIPTION];
    pre.scrollIntoView();
  }

  // 'services-enabled' event listener

  window.app.addListener('services-enabled', function(msg)
  {
    window.services['window-manager'].requestListWindows();
    window.services['window-manager'].requestModifyFilter(0, [1, [], ['*']]);
  });
 
}
 