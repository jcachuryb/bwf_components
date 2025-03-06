/* eslint-disable prefer-spread */
/* eslint-disable no-plusplus */
class ValueSelector {
  constructor(element, settings, $) {
    const _ = this;

    _.defaults = {
      name: "DBCA-BWF-VARIABLE-SELECTOR",
      theme: "default",
    };

    const { input, component } = settings;
    const { value, json_value, data_type } = input;
    const { type, options, value_rules } = json_value || {};

    _.component = component;

    _.initials = {
      present: true,
      value: value,
      type: type,
      options: options,
      value_rules: value_rules,
    };
    const elementSettings = {
      type,
      options,
      value_rules,
    };
    _.options = $.extend({}, _.defaults, elementSettings);

    $.extend(_, _.initials);
    _.$element = $(element);
    _.render(elementSettings, value);
  }

  render(elementSettings, value) {
    const _ = this;
    const { markup } = utils;
    const $vars = workflow_variables;
    const $inputs = workflow_inputs;

    const { type, options, value_rules } = elementSettings;

    if (value_rules && value_rules.variable_only) {
      _.$element.empty();
      const selectElement = markup(
        "select",
        [
          markup("option", "Select a variable", { value: "" }),
          ...$vars.var.variables.map((variable) =>
            markup("option", variable.name, { value: variable.key })
          ),
        ],
        {
          class: "form-select",
          value: value ?? "",
        }
      );
      _.$element.append(selectElement);
      $(selectElement).on("change", { change: () => {} }, function (event) {
        const selectedValue = event.target.value;
        console.log(selectedValue);
      });
    } else {
      _.$element.addClass("value-selector");
      const popoverOptions = {
        html: true,
        title: "<h1>aaaa</h1>",
        content: $('[data-name="popover-content"]').clone(),
      };

      var popover = new bootstrap.Popover(_.$element, popoverOptions);
      _.$element.on("click", _, function (event) {
        const selector = event.data;
      });
    }
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
    if (typeof opt === "object" || typeof opt === "undefined") {
      _[i].formb = new ValueSelector(_[i], opt, jQuery);
    } else {
      ret = _[i].formb[opt].apply(_[i].formb, moreArgs, jQuery);
    }
    if (typeof ret !== "undefined") return ret;
  }
  return _;
};
