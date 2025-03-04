/* eslint-disable prefer-spread */
/* eslint-disable no-plusplus */
class ValueSelector {
  constructor(element, settings, $) {
    const _ = this;

    _.defaults = {
      name: 'DBCA-BWF-VARIABLE-SELECTOR',
      theme: 'default',

    };

    const { type, options, value_rules } = settings


    _.initials = {
      present: true,
      type: type,
      options: options,
      value_rules: value_rules,
    };

    $.extend(_, _.initials);

    _.$element = $(element);
    _.$element.addClass('value-selector');
    // _.$element.attr('data-name', _.name);
    _.options = $.extend({}, _.defaults, settings);

    

    const popoverOptions = {
      html: true,
      title: "",
      //html element
      //content: $("#popover-content")
      content: $('[data-name="popover-content"]')
      //Doing below won't work. Shows title only
      //content: $("#popover-content").html()

  }
  
  var popover = new bootstrap.Popover(_.$element, popoverOptions)
  }

  render(options) {
    const _ = this;
    _.$element.on('click', function () {

      
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

jQuery.fn.valueSelector = function (...args) {
  const _ = this;
  const opt = args[0];
  const moreArgs = Array.prototype.slice.call(args, 1);
  const l = _.length;
  let i;
  let ret;

  for (i = 0; i < l; i++) {
    if (typeof opt === 'object' || typeof opt === 'undefined') {
      _[i].formb = new ValueSelector(_[i], opt, jQuery);
    } else {
      ret = _[i].formb[opt].apply(_[i].formb, moreArgs, jQuery);
    }
    if (typeof ret !== 'undefined') return ret;
  }
  return _;
};