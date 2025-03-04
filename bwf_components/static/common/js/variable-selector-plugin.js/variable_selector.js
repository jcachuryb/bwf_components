/* eslint-disable prefer-spread */
/* eslint-disable no-plusplus */
class VariableSelector {
  constructor(element, settings, $) {
    const _ = this;

    _.defaults = {
      name: 'DBCA-BWF-VARIABLE-SELECTOR',
      theme: 'default',

    };

    _.initials = {
      present: true,
      
    };

    $.extend(_, _.initials);

    _.$element = $(element);
    _.options = $.extend({}, _.defaults, settings);
    
  }

  render(options) {
    const _ = this;
    _.$element.on('click', function () {
debugger
    })
  }

  onSubmit() {}

  getJSON() {
    return this.layout.buildArea.toJSON();
  }

  widget() {
    return this;
  }
}

jQuery.fn.variableSelector = function (...args) {
  const _ = this;
  const opt = args[0];
  const moreArgs = Array.prototype.slice.call(args, 1);
  const l = _.length;
  let i;
  let ret;

  for (i = 0; i < l; i++) {
    if (typeof opt === 'object' || typeof opt === 'undefined') {
      _[i].formb = new VariableSelector(_[i], opt, jQuery);
    } else {
      ret = _[i].formb[opt].apply(_[i].formb, moreArgs, jQuery);
    }
    if (typeof ret !== 'undefined') return ret;
  }
  return _;
};
