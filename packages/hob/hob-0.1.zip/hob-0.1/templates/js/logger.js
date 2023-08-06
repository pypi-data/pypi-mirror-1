window.cls || ( window.cls = {} );

/**
  * @constructor 
  */

window.cls.Logger = function()
{
  // singleton
  if(arguments.callee.instance)
  {
    return arguments.callee.instance;
  }
  arguments.callee.instance = this;

  this.log = function(/* arg 1, arg 2, ... */)
  {
    _log([].slice.call(arguments).join(' ') + '\n');
  }

  this.log_error = function(/* arg 1, arg 2, ... */)
  {
    _log("<span class='error'>" + [].slice.call(arguments).join(' ') + "\n</span>");
  }

  var _log = function(str)
  {
    _log_container.innerHTML += str;
    _log_container_parent.scrollTop = _log_container_parent.scrollHeight;
  }

  var _log_container = null;
  var _log_container_parent = null;
  var _init = function()
  {
    _log_container = document.getElementsByTagName('pre')[0];
    _log_container_parent = _log_container.parentNode;
  }

  _init();

}