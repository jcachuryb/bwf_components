/* eslint-disable prefer-spread */
/* eslint-disable no-plusplus */
class ValueSelector {
  constructor(element, settings, $) {
    const _ = this;
    const { markup } = utils;

    _.defaults = {
      name: "DBCA-BWF-VARIABLE-SELECTOR",
      theme: "default",
    };

    const { input, component } = settings;

    if (!input || !component) {
      return;
    }

    const { json_value, data_type } = input;
    const { type, options, value_rules } = json_value || {};
    const { value_ref, value, is_expression } = input.value ?? {};

    _.component = component;
    _.input = input;

    _.initials = {
      present: true,
      value: value,
      value_ref: value_ref,
      type: type,
      options: options,
      value_rules: value_rules,
      is_expression: !!is_expression,
      showEditor: !!is_expression,
    };
    const elementSettings = {
      type,
      options,
      value_rules,
    };
    _.options = $.extend({}, _.defaults, elementSettings);

    $.extend(_, _.initials);
    _.$element = $(element);

    const content = markup("div", "", {
      "data-id": `${component.id}-${input.key}`,
      class: "value-selector-content me-1",
    });
    const resetButton = markup("button", [{ tag: "i", class: "bi bi-trash" }], {
      class: "btn btn-sm btn-outline-secondary value-selector-reset",
    });
    const editButton = markup("button", [{ tag: "i", class: "bi bi-pencil" }], {
      class: "btn btn-sm btn-primary value-selector-edit me-1",
    });
    _.$element.append(content);
    _.$element.append(editButton);
    _.$element.append(resetButton);

    _.$content = _.$element.find(".value-selector-content");
    _.$resetButton = _.$element.find(".value-selector-reset");
    _.$editButton = _.$element.find(".value-selector-edit");
    _.$saveButton = null;

    _.updateHtml();
    _.render(value, value_ref);
  }

  render(value, value_ref = {}) {
    const _ = this;
    const { markup } = utils;
    const $vars = workflow_variables;

    const { type, options, value_rules } = _.input?.json_value ?? {};

    if (value_rules && value_rules.variable_only) {
      _.$content.empty();
      _.$resetButton.hide();
      _.$editButton.hide();
      const selectElement = markup(
        "select",
        [
          markup("option", "Select a variable", { value: "" }),
          ...$vars.var.variables.map((variable) => {
            const opts = {
              value: variable.id,
              "data-context": variable.context ?? "variables",
              "data-name": variable.name,
              "data-key": variable.key,
            };
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
      _.$content.append(selectElement);

      $(selectElement).on(EVENT_VARIABLES_CHANGE, _, (event) => {
        const selector = event.data;
        selector.render(selector.input.value, {});
      });
      $(selectElement).on("change", _, function (event) {
        const selector = event.data;
        const selectedValue = event.target.value;
        const context =
          $(event.target).find("option:selected").data("context") ??
          "variables";
        const name =
          $(event.target).find("option:selected").data("name") ?? "undefined";
        const key = $(event.target).find("option:selected").data("key");
        selector.saveValue({
          value: selectedValue,
          is_expression: false,
          value_ref: null,
        });
      });
    } else if (options) {
      _.$content.empty();
      _.$resetButton.hide();
      _.$editButton.hide();

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
      _.$content.append(selectElement);

      $(selectElement).on("change", _, function (event) {
        const selector = event.data;
        const selectedValue = event.target.value;
        selector.saveValue({
          value: selectedValue,
          is_expression: false,
          value_ref: null,
        });
      });
    } else {
      // render popover
      _.renderPopover();
    }
  }

  onPopoverOpen() {
    const _ = this;
    console.log({ settings: _.initials });
    const { input, component } = _;
    const { value, value_ref, is_expression } = input.value ?? {};
    const { type, options, value_rules } = _.input?.json_value ?? {};
    if ((!value || value_ref) && !_.initials.showEditor) {
      _.$saveButton.hide();
    } else {
      _.$saveButton.show();
    }

    if (_.editor) {
      if (!value && !value_ref) {
        _.editor.setValue("");
      }
      if (value) _.editor.setValue(value);
      if (!value && value_ref) {
        _.editor.setValue(`$${value_ref.context}['${value_ref.key}']`);
      }
    }
  }

  renderPopover() {
    const _ = this;
    const { input, component } = _;
    const { markup } = utils;
    const $vars = workflow_variables;
    const $inputs = workflow_inputs;

    const { type, options, value_rules } = _.input?.json_value ?? {};
    const { value, value_ref, is_expression } = input.value ?? {};

    if (value) {
      _.$resetButton.show();
      _.$resetButton.on("click", _, function (event) {
        const selector = event.data;
        selector.saveValue({
          value: null,
          is_expression: false,
          value_ref: null,
        });
      });
    } else {
      _.$resetButton.off("click");
      _.$resetButton.hide();
    }
    _.$editButton.show();
    _.$editButton.on("click", _, function (event) {
      const selector = event.data;
      _.initials.showEditor = true;
      selector.popover.show();
    });
    // _.$resetButton.hide();
    // _.$editButton.hide();
    const popoverContent = $('[data-name="popover-content"]').clone();

    _.$content.addClass("value-selector");
    _.$saveButton = popoverContent.find(".btn-save");

    popoverContent.attr("data-name", null);
    popoverContent.attr("id", `popover-content-${component.id}-${input.key}`);
    popoverContent
      .find(".context-menu")
      .attr("id", `context-menu-${component.id}-${input.key}`);

    _.$saveButton.on("click", _, function (event) {
      const selector = event.data;
      const selectedValue = selector.editor?.getValue();
      selector.saveValue({
        value: selectedValue,
        is_expression: true,
        value_ref: null,
      });
    });

    popoverContent.find(".btn-close").on("click", _, function (event) {
      const selector = event.data;
      selector.editor?.setValue(selector.input.value?.value ?? "");
      selector.popover.hide();
    });

    popoverContent
      .find(".editor")
      .attr("id", `editor-${component.id}-${input.key}`);
    // POPOVER
    const popoverOptions = {
      html: true,
      title: `${component.name}: ${input.name}`,
      content: popoverContent,
      placement: "top",
    };
    _.popover = new bootstrap.Popover(_.$content, popoverOptions);

    _.$content.on("click", _, function (event) {
      const selector = event.data;
    });
    _.$content.on("shown.bs.popover", _, function (event) {
      const _ = event.data;
      const { input, component } = _;
      const { value, is_expression } = input.value ?? {};
      if (_.initials.showEditor)
        _.setUpEditor(`editor-${component.id}-${input.key}`);

      $(`#context-menu-${component.id}-${input.key}`).contextMenu({
        input,
        component,
        showInPopover: !!is_expression || _.initials.showEditor,
        onSelectValue: (value) => {
          console.log("Selected value", value);
          if (_.initials.showEditor && _.editor) {
            const doc = _.editor.getDoc();
            const cursor = doc.getCursor();
            doc.replaceRange(`$${value?.context}['${value?.key}']`, cursor);
          } else {
            _.saveValue({
              value: null,
              is_expression: false,
              value_ref: {
                context: value.context,
                key: value.key,
                id: value.id,
              },
            });
          }
        },
      });
    });
    _.$content.on("show.bs.popover", _, function (event) {
      $(".popover.show").each(function () {
        // hide any open popovers when the anywhere else in the body is clicked
        if (
          !$(this).is(_.$content) &&
          $(this).has(_.$content).length === 0 &&
          $(".popover").has(_.$content).length === 0
        ) {
          $(this).popover("hide");
        }
      });
      const selector = event.data;
      selector.onPopoverOpen();
    });
  }

  setUpEditor(editorId) {
    const _ = this;
    const { input, component } = _;
    const { value, value_ref, is_expression } = input.value ?? {};
    const { type, options, value_rules } = _.input?.json_value ?? {};
    if (!_.editor) {
      _.editor = CodeMirror.fromTextArea($(`#${editorId}`)[0], {
        doc: "Start document",
        value: "",
        mode: "python",
        placeholder: "Enter a value",
        theme: "default",
        lineNumbers: true,
        styleActiveLine: true,
        matchBrackets: true,
        autoCloseBrackets: true,
        lineWrapping: true,
      });
      if (value) _.editor.setValue(value);
      if (!value && value_ref) {
        _.editor.setValue(`$${value_ref.context}['${value_ref.key}']`);
      }

      _.editor.setOption("extraKeys", {
        "Ctrl-Space": "autocomplete",
        "Ctrl-Enter": function (cm) {
          _.saveValue({
            value: cm.getValue(),
            is_expression: true,
            value_ref: null,
          });
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
    const body = {
      component_id: component.id,
      plugin_id: component.plugin_id,
      plugin_version: component.plugin_version,
      id: input.id,
      key: input.key,
      value: value,
    };
    workflow_components.api.updateComponentInputValue(
      body,
      (data) => {
        const selector = this;
        const { key, value, json_value } = data;
        selector.input = data;
        workflow_components.updateInputValue(
          selector.component.id,
          key,
          value,
          json_value
        );

        selector.updateHtml();
        if (popover) popover.hide();
        console.log("updated", data);
      },
      (error) => {
        console.error(error);
      }
    );
  }

  updateValue(value, json_value) {
    const _ = this;
    _.input.value = value;
    _.input.json_value = json_value;
    _.updateHtml();
  }

  updateHtml() {
    const _ = this;
    const { input, component } = _;
    const { value, json_value } = input;
    const { type, options, value_rules } = json_value ?? {};

    if ((value_rules && value_rules.variable_only) || options) {
      _.$resetButton.hide();
      _.$editButton.hide();
      return;
    }
    _.$content.empty();
    if (value && value.value_ref) {
      const { context: ref_context, key: ref_key } = value.value_ref;
      _.$content.html(`$${ref_context}['${ref_key}']`);
    } else {
      _.$content.html(value.is_expression ? "Editor" : "");
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
