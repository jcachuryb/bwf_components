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
    _.input = input;

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

    _.render(value);
  }

  render(value) {
    const _ = this;
    const { input, component } = _;
    const { markup } = utils;
    const $vars = workflow_variables;
    const $inputs = workflow_inputs;

    const { type, options, value_rules } = _.input?.json_value ?? {};

    if (value_rules && value_rules.variable_only) {
      _.$element.empty();
      const selectElement = markup(
        "select",
        [
          markup("option", "Select a variable", { value: "" }),
          ...$vars.var.variables.map((variable) => {
            const opts = { value: variable.id };
            if (variable.id === value) {
              opts.selected = true;
            }
            return markup("option", variable.name, opts);
          }),
        ],
        {
          class: "form-select variables-select",
          value: value ?? "",
        }
      );
      _.$element.append(selectElement);

      $(selectElement).on("change", _, function (event) {
        const selector = event.data;
        const { input, component } = selector;
        const selectedValue = event.target.value;

        const data = {
          id: component.id,
          plugin_id: component.plugin_id,
          plugin_version: component.plugin_version,
          key: input.key,
          value: selectedValue,
        };
        workflow_components.api.updateComponentInputValue(
          data,
          (data) => {
            console.log("updated", data);
          },
          (error) => {
            console.error(error);
          }
        );
      });

      $(selectElement).on(EVENT_VARIABLES_CHANGE, _, (event) => {
        const selector = event.data;
        selector.render(selector.input.value);
      });
    } else {
      _.$element.addClass("value-selector");
      const popoverContent = $('[data-name="popover-content"]').clone();
      popoverContent.attr("data-name", null);
      popoverContent.attr("id", `popover-content-${input.key}`);
      const popoverOptions = {
        html: true,
        title: "",
        content: popoverContent,
      };

      var popover = new bootstrap.Popover(_.$element, popoverOptions);
      var editor = CodeMirror(popoverContent.find(".editor")[0], {
        doc: "Start document",
        value: "# Hello world\nprint('yea')",
        mode: "python",
      });

      _.$element.on("click", _, function (event) {
        const selector = event.data;
      });
      _.$element.on("show.bs.popover", _, function (event) {
        // const popover = bootstrap.Popover.getOrCreateInstance('.popover.show');
        // if(popover) {
        //   popover.hide();
        // }
        const selector = event.data;
        selector.onPopoverOpen();
      });
    }
  }

  onPopoverOpen() {
    const _ = this;
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
