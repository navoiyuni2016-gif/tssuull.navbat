'use strict';
// Compatibility for X96 WebViews that parse modern JS but predate DOM replaceChildren.
(function () {
  function define(target, name, value) {
    if (target && typeof target[name] !== 'function') {
      Object.defineProperty(target, name, {value: value, writable: true, configurable: true});
    }
  }
  function replaceChildren() {
    var nodes = [], i;
    for (i = 0; i < arguments.length; i++) {
      nodes.push(arguments[i] && typeof arguments[i] === 'object' && arguments[i].nodeType ? arguments[i] : document.createTextNode(String(arguments[i])));
    }
    while (this.firstChild) this.removeChild(this.firstChild);
    for (i = 0; i < nodes.length; i++) this.appendChild(nodes[i]);
  }
  define(window.Element && Element.prototype, 'replaceChildren', replaceChildren);
  define(window.Document && Document.prototype, 'replaceChildren', replaceChildren);
  define(window.DocumentFragment && DocumentFragment.prototype, 'replaceChildren', replaceChildren);
  if (window.Animation && !('finished' in Animation.prototype)) {
    Object.defineProperty(Animation.prototype, 'finished', {configurable: true, get: function () {
      var animation = this;
      return new Promise(function (resolve) {
        if (animation.playState === 'finished') { resolve(animation); return; }
        function done() { animation.removeEventListener('finish', done); animation.removeEventListener('cancel', done); resolve(animation); }
        animation.addEventListener('finish', done); animation.addEventListener('cancel', done);
      });
    }});
  }
  define(Object, 'fromEntries', function (entries) {
    var result = {}, i, pair;
    if (!entries || typeof entries.length !== 'number') throw new TypeError('Entries array required');
    for (i = 0; i < entries.length; i++) {
      pair = entries[i];
      Object.defineProperty(result, String(pair[0]), {value: pair[1], enumerable: true, configurable: true, writable: true});
    }
    return result;
  });
}());
