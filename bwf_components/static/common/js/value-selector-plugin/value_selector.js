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
    _.$element.html(value);

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
          class: "form-select form-select-sm variables-select",
          value: value ?? "",
        }
      );
      _.$element.append(selectElement);

      $(selectElement).on(EVENT_VARIABLES_CHANGE, _, (event) => {
        const selector = event.data;
        selector.render(selector.input.value);
      });
      $(selectElement).on("change", _, function (event) {
        const selector = event.data;
        const selectedValue = event.target.value;
        selector.saveValue(selectedValue);
      });
    } else if (options) {
      _.$element.empty();
      const selectElement = markup(
        "select",
        [
          markup("option", "Select a variable", { value: "" }),
          ...options.map((option) => {
            const opts = { value: option.value };
            if (option.value === value) {
              opts.selected = true;
            }
            return markup("option", option.label, opts);
          }),
        ],
        {
          class: "form-select form-select-sm variables-select",
          value: value ?? "",
        }
      );
      _.$element.append(selectElement);

      $(selectElement).on("change", _, function (event) {
        const selector = event.data;
        const selectedValue = event.target.value;
        selector.saveValue(selectedValue);
      });
    } else {
      _.$element.addClass("value-selector");
      const popoverContent = $('[data-name="popover-content"]').clone();
      popoverContent.attr("data-name", null);
      popoverContent.attr("id", `popover-content-${input.key}`);
      popoverContent
        .find(".context-menu")
        .attr("id", `context-menu-${input.key}`);
      popoverContent.find(".btn-save").on("click", _, function (event) {
        const selector = event.data;
        const selectedValue = selector.editor.getValue();
        selector.saveValue(selectedValue);
      });
      popoverContent.find(".btn-close").on("click", _, function (event) {
        const selector = event.data;
        selector.editor.setValue(selector.input.value);
        selector.popover.hide();
      });
      popoverContent.find(".editor").attr("id", `editor-${input.key}`);
      const popoverOptions = {
        html: true,
        title: "",
        content: popoverContent,
        placement: "top",
      };
      _.popover = new bootstrap.Popover(_.$element, popoverOptions);

      _.$element.on("click", _, function (event) {
        const selector = event.data;
      });
      _.$element.on("shown.bs.popover", _, function (event) {
        const _ = event.data;
        const { input, component } = _;
        _.setupMenu();
        // _.setUpEditor();
      });
      _.$element.on("show.bs.popover", _, function (event) {
        $(".popover.show").each(function () {
          // hide any open popovers when the anywhere else in the body is clicked
          if (
            !$(this).is(_.$element) &&
            $(this).has(_.$element).length === 0 &&
            $(".popover").has(_.$element).length === 0
          ) {
            $(this).popover("hide");
          }
        });
        const selector = event.data;
        selector.onPopoverOpen();
      });
    }
  }

  onPopoverOpen() {
    const _ = this;
  }
  setupMenu() {
    const _ = this;
    const { markup } = utils;
    const { input, component } = _;
    const value = input.value;
    const { type, options, value_rules } = _.input?.json_value ?? {};

    const menuElements = markup("ul", [
      // inputs,
      {
        tag: "li",
        content: [
          markup("div", "Inputs"),
          markup(
            "ul",
            workflow_inputs.var.inputs.map((el) => ({
              tag: "li",
              content: el.label,
              class: "",
              "data-value": el.id,
              "data-key": el.key,
            }))
          ),
        ],
      },
      // variables
      {
        tag: "li",
        content: [
          markup("div", "Variables"),
          markup(
            "ul",
            workflow_variables.var.variables.map((el) => ({
              tag: "li",
              content: el.name,
              class: "",
              "data-value": el.id,
              "data-key": el.key,
            }))
          ),
        ],
      },
    ]);

    $(`#context-menu-${input.key}`).empty();
    $(`#context-menu-${input.key}`).append(menuElements.children);
    $(`#context-menu-${input.key}`).menu();
    $(`#context-menu-${input.key}`).show();
  }
  setUpEditor() {
    const _ = this;
    const { input, component } = _;
    const value = input.value;
    const { type, options, value_rules } = _.input?.json_value ?? {};
    if (!_.editor) {
      _.editor = CodeMirror.fromTextArea($(`#editor-${input.key}`)[0], {
        doc: "Start document",
        value: value,
        mode: "python",
        placeholder: "Enter a value",
        theme: "default",
        lineNumbers: true,
        styleActiveLine: true,
        matchBrackets: true,
        autoCloseBrackets: true,
        lineWrapping: true,
      });

      _.editor.setOption("extraKeys", {
        "Ctrl-Space": "autocomplete",
        "Ctrl-Enter": function (cm) {
          _.saveValue(cm.getValue());
        },
      });
    }

    function getHints(cm, option) {
      return new Promise(function (accept) {
        setTimeout(function () {
          var cursor = cm.getCursor(),
            line = cm.getLine(cursor.line);
          var start = cursor.ch,
            end = cursor.ch;
          while (start && /(\$|\w)/.test(line.charAt(start - 1))) --start;
          while (end < line.length && /(\$)\w/.test(line.charAt(end))) ++end;
          var word = line.slice(start, end).toLowerCase();
          if (word === "" || word.startsWith("$")) return accept(null);

          const vars = workflow_variables.var.variables
            .filter((v) => v.key.startsWith(word))
            .map((v) => `${v.context}['${v.key}']`);

          const inputs = workflow_inputs.var.inputs
            .filter((v) => v.key.startsWith(word))
            .map((v) => `$inputs['${v.key}']`);
          const local = [];

          // TODO: Get values from output
          return accept({
            list: vars.concat(inputs),
            from: CodeMirror.Pos(cursor.line, start),
            to: CodeMirror.Pos(cursor.line, end),
          });
        }, 100);
      });
    }

    _.editor.setOption("hintOptions", {
      hint: getHints,
    });
  }

  saveValue(value) {
    const { input, component, $element, popover } = this;
    const data = {
      id: component.id,
      plugin_id: component.plugin_id,
      plugin_version: component.plugin_version,
      key: input.key,
      value: value,
    };
    workflow_components.api.updateComponentInputValue(
      data,
      (data) => {
        this.updateHtml();
        if (popover) popover.hide();
        console.log("updated", data);
      },
      (error) => {
        console.error(error);
      }
    );
  }

  updateHtml() {
    const _ = this;
    const { input, component } = _;
    const { value, json_value } = input;
    const { type, options, value_rules } = json_value ?? {};

    if ((value_rules && value_rules.variable_only) || options) {
      return;
    }
    _.$element.empty();
    _.$element.html(value);
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
