var workflow_components = {
  workflow_id: null,
  version_id: null,
  is_edition: true,
  is_diagram: false,
  has_init: false,
  add_component_btn: null,
  containerId: null,
  container: null,
  firstLine: null,
  sidePanel: null,

  selectedComponent: null,
  var: {
    base_url: "/bwf/api/workflow-components/",
    components: [],
    definitions: [],
    incoming: [],
  },
  pluginDefinitions: [],

  init: function (options, containerId) {
    const { workflow_id, version_id, is_edition, is_diagram, sidePanel } =
      options;
    const _ = workflow_components;
    if (!workflow_id || !version_id || !containerId) {
      console.error("workflow_id and containerId are required");
      console.error("workflow_id is required");
      return;
    }
    _.workflow_id = workflow_id;
    _.version_id = version_id;
    _.containerId = containerId;

    _.is_edition = is_edition;
    _.is_diagram = is_diagram;

    _.container = $(`#${containerId}`);
    _.sidePanel = sidePanel;
    // Add + Buttton
    const _params = {
      workflow_id: _.workflow_id,
      version_id: _.version_id,
    };
    const queryParams = utils.make_query_params(_params);
    $.ajax({
      url: _.var.base_url + "?" + queryParams,
      type: "GET",
      success: function (data) {
        _.var.components = data;
        if (data.length > 0) {
          $(".main-add-component").hide();
        } else {
          $(".main-add-component").show();
        }
        _.renderComponents();
      },
      error: function (error) {
        console.error(error);
      },
    });
    _.has_init = true;
  },
  renderComponents: function () {
    const _ = workflow_components;
    const components = _.var.components;
    // entry point
    if (components.length === 0) {
      return;
    }

    const entry_point = components.find(
      (component) => component.conditions.is_entry
    );
    if (!entry_point) {
      throw new Error("Workflow doesn't have an entry point.");
    }
    // Build COmponents graph
    let component = entry_point;
    const nodeIds = {};
    components.forEach((component) => {
      nodeIds[component.id] = component;
    });
    do {
      if (Object.keys(nodeIds).length === 0 || !component) {
        break;
      }
      if (nodeIds[component.id]) {
        _.appendComponent(component);
        $(".component-node, .diagram-node-parent").draggable({});
        if (component.config.branch) {
          // draw branch
          const branch = component.config.branch;
          const branchTrue = branch.True;
          const branchFalse = branch.False;

          const template = document.querySelector("#component-branch-template");
          const clone = template.content.cloneNode(true);
          const branchElemId = `branch_${component.id}`;
          clone.querySelector("div").id = branchElemId;

          // $(`#node_${component.id}`).find('.component-dot-add').remove();
          $(`#node_${component.id}`).after(clone);

          // $(`#node_${component.id}`).find(".branch-true").html(branchTrue);
          const start = $(`#node_${component.id} .component-dot-add`);
          const lines = [
            {
              start: start,
              end: $(`#${branchElemId} .branch-true`),
              color: "#0d6efd",
              label: "True",
            },
            {
              start: start,
              end: $(`#${branchElemId} .branch-false`),
              color: "#dc3545",
              label: "False",
            },
          ];
          lines.forEach((line) => {
            const line_out = new LeaderLine(line.start[0], line.end[0], {
              color: line.color,
              size: 2,
              middleLabel: line.label,
            });
          });
        }

        delete nodeIds[component.id];
      }
      if (component.conditions.route) {
        const route = component.conditions.route;
        const next_component = components.find(
          (component) => component.id === route
        );
        if (!next_component) {
          console.error("Route not found", route);
          component = nodeIds[Object.keys(nodeIds)[0]];
          continue;
          // break;
        }
        component = next_component;
      } else {
        component = null;
      }
    } while (component);

    for (let i = 0; i < components.length; i++) {
      const component = components[i];
      if (i === 0) {
        _.renderFirstLine(component);
        $(`#node_${component.id}`).find(".btn-dropdown").trigger("click");
      }
      _.renderRouteLine(component);
    }
    const container = $("body");

    var scrollTo = $("#components-flow");
    var position =
      scrollTo.offset().top - container.offset().top + container.scrollTop();
    container.scrollTop(position);
  },
  renderFirstLine: function (component) {
    const _ = workflow_components;
    _.firstLine = new LeaderLine(
      $(`#flow-start-node`)[0],
      $(`.component-node, .diagram-node`)[0],
      {
        color: "#6cb0be",
        size: 2,
      }
    );
    $(`#node_${component.id}`).on("drag.first_line", _, (event) => {
      const _ = event.data;
      _.firstLine.position();
    });
  },
  renderRouteLine: function (component) {
    const _ = workflow_components;
    if (component.conditions.route) {
      const route = component.conditions.route;
      const start = $(`#node_${component.id} .component-route.component-out`);
      const end = $(`#node_${route} .diagram-node`);
      if (start.length > 0 && end.length > 0) {
        const components = _.var.components;
        const destination = components.find(
          (component) => component.id === route
        );

        try {
          destination.diagram?.line_in?.remove();
        } catch (error) {}

        const line = new LeaderLine(start[0], end[0], {
          color: "#6cb0be",
          size: 2,
          // middleLabel: `${component.name} -> ${destination.name}`,
        });

        component.diagram = component.diagram || {};
        component.diagram.line_out = line;
        destination.diagram = destination.diagram || {};
        destination.diagram.line_in = line;
        $(`#node_${component.id}`).on(
          "drag.line_out",
          { isSource: true, id: component.id },
          _.handleLineDrag
        );
        $(`#node_${route}`).on(
          "drag.line_in",
          { isSource: false, id: route },
          _.handleLineDrag
        );
      }
    }
  },
  handleLineDrag: function (event, ui) {
    const components = workflow_components.var.components;
    const isSource = event.data.isSource;
    const componentId = event.data.id;
    const component = components.find(
      (component) => component.id === componentId
    );

    if (isSource) {
      try {
        component.diagram.line_out?.position();
      } catch (e) {}
    } else {
      try {
        component.diagram.line_in?.position();
      } catch (e) {}
    }
  },
  appendComponentToDiagram: function (component, appendAfter) {
    const template = document.querySelector("#component-diagram-node-template");
    const { markup } = utils;

    const { id, name } = component;
    const { inputs, outputs } = component.config;
    const inputArray = inputs || [];
    const outputArray = outputs || [];
    // Clone the new row and insert it into the table
    const clone = template.content.cloneNode(true);
    const _ = workflow_components;
    const elementId = `node_${id}`;
    clone.querySelector(".diagram-node-parent").setAttribute("id", elementId);
    clone.querySelector(".diagram-node").setAttribute("data-component-id", id);

    if (appendAfter) {
      appendAfter.after(clone);
    } else {
      _.container.append(clone);
    }

    $(`#${elementId}`)
      .find(".component-icon")
      .html(
        markup("i", "", {
          class: component.ui?.class_name ?? "bi bi-gear",
        })
      );
    $(`#${elementId}`).find(".component-label span").html(name);
    if (!_.is_edition) {
      $(`#${elementId}`).find(".delete-component").remove();
      $(`#${elementId}`).find(".add-next-component").remove();
    }
    _.addMenuDiagramNodeFunctionality(elementId, component);
  },

  appendComponent: function (component, appendAfter) {
    const _ = workflow_components;
    if (_.is_diagram) {
      _.appendComponentToDiagram(component, appendAfter);
      return;
    }
    const template = document.querySelector("#component-node-template");
    const { markup } = utils;

    const { id, name } = component;
    const { inputs, outputs } = component.config;
    const inputArray = inputs || [];
    const outputArray = outputs || [];
    // Clone the new row and insert it into the table
    const clone = template.content.cloneNode(true);
    const elementId = `node_${id}`;
    clone.querySelector(".component-node").setAttribute("id", elementId);
    clone
      .querySelector(".component-node")
      .setAttribute("data-component-id", id);

    if (appendAfter) {
      appendAfter.after(clone);
    } else {
      _.container.append(clone);
    }

    if (!_.is_edition) {
      $(`#${elementId}`).find(".delete-component").remove();
      $(`#${elementId}`).find(".add-next-component").remove();
    }

    $(`#${elementId}`).find(".component-label").html(name);
    for (let i = 0; i < inputArray.length; i++) {
      const input = inputArray[i];
      const divElementId = `${elementId}_${input.key}`;
      const inputElement = _.getComponentInputElement({
        ...input,
        elementId: divElementId,
      });
      $(`#${elementId}`).find(".list-group.input").append(inputElement);

      $(
        `#${divElementId}.input-value, #${divElementId}_array .input-value`
      ).valueSelector({
        input: input,
        component: component,
        isEdition: _.is_edition,
        portal: $(body).find(".panel-value-edition"),
      });
    }
    if (outputArray.length > 0) {
      $(`#${elementId}`).find(".list-group.output").show();
    }
    for (let i = 0; i < outputArray.length; i++) {
      const output = outputArray[i];
      const divElementId = `${elementId}_${output.key}`;
      const outputElement = _.getComponentOutputElement({
        ...output,
      });
      $(`#${elementId}`).find(".list-group.output").append(outputElement);
    }
    _.addMenuButtonsFunctionality(elementId, component);
  },
  addMenuDiagramNodeFunctionality: function (elementId, component) {
    $(`#${elementId}`)
      .find(".component-label")
      ?.on("click", component, function (event) {
        const _ = workflow_components;
        const { id } = event.data;
        const component = _.var.components.find(
          (component) => component.id === id
        );
        if (!component) return;
        _.renderComponentSidePanel(component);
      });

    $(`#${elementId}`)
      .find(".add-next-component, .component-route.component-out")
      ?.on("click", component, function (event) {
        new_component_data.selectedComponent.data = event.data;
        $("#component-creation-modal").modal("show");
      });
  },
  addComponentSettingsFunctionality: function (component) {
    const _ = this;
    $(`#component-settings-form`)
      .find(".component-name")
      ?.on("change", component, function (event) {
        $(this).trigger("blur");
      });
    $(`#component-settings-form`).on("submit", component, function (event) {
      event.preventDefault();
      event.stopPropagation();
      const component = event.data;
      const _ = workflow_components;
      const name = $(`#component-settings-form .component-name`).val().trim();
      if (!name || name == component.name) {
        return;
      }
      $(`#component-settings-form button, #component-settings-form input`).prop(
        "disabled",
        true
      );
      const data = {
        id: component.id,
        plugin_id: component.plugin_id,
        name: name,
      };
      _.api.updateComponent(
        data,
        function (data) {
          const _component = _.var.components.find((c) =>
            c.id === component.id ? data : c
          );
          _component.name = name;
          $(`#node_${component.id}`).find(".component-label span").html(name);
          $(`#node_panel_${component.id}`).find(".component-label").html(name);
          $(
            `#component-settings-form button, #component-settings-form input`
          ).prop("disabled", false);
          $(`#component-settings-form`).hide();
          $(`#node_panel_${component.id}`).show();
        },
        function (error) {
          $(
            `#component-settings-form button, #component-settings-form input`
          ).prop("disabled", false);
        }
      );
    });

    $(`#component-settings-form button.cancel-btn`).on(
      "click",
      component,
      function (event) {
        event.preventDefault();
        event.stopPropagation();
        $(`#component-settings-form`).hide();
        $(`#node_panel_${component.id}`).show();
      }
    );
  },
  addMenuButtonsFunctionality: function (elementId, component) {
    // Delete Component
    $(`#${elementId}`)
      .find(".delete-component")
      ?.on("click", component, function (event) {
        const _ = workflow_components;
        const { id } = event.data;
        const data = {
          id: id,
          workflow_id: _.workflow_id,
          version_id: _.version_id,
        };
        _.api.deleteComponent(data, function (data) {
          $(`#node_${component.id}`).remove();
          $(`#${elementId}`).remove();
          workflow_components.removeComponent(id);
          _.sidePanel?.close();
        });
      });
    // END: Delete Component

    $(`#${elementId}`)
      .find(".print-component")
      ?.on("click", component, function (event) {
        const _ = workflow_components;
        const { id } = event.data;
        const component = _.var.components.find(
          (component) => component.id === id
        );
        console.log({ component });
      });
    $(`#${elementId}`)
      .find(".edit-component")
      ?.on("click", component, function (event) {
        const _ = workflow_components;
        const { id } = event.data;
        const component = _.var.components.find(
          (component) => component.id === id
        );
        $(`#component-settings-form`)
          .find(".component-name")
          .val(component.name);
        $(`#component-settings-form`).show();
        $(`#node_panel_${component.id}`).hide();

      });
  },
  getComponentInputElement: function (input) {
    const _ = this;
    const { markup } = utils;
    const {
      id,
      elementId,
      name,
      key,
      data_type,
      expression,
      json_value,
      index,
      required,
    } = input;
    const multi = json_value?.multi || false;
    const variable_only = json_value?.variable_only || false;
    const value_only = json_value?.value_only || false;
    const options = json_value?.options || [];
    const default_value = json_value?.default_value || "";
    const value_rules = json_value?.value_rules;

    let element = markup("div", "", {
      id: elementId,
      name: key,
      class: "input-value",
    });
    const items = [];
    const container = markup(
      "div",
      [
        multi
          ? ""
          : markup(
              "div",
              markup("label", name, { for: key, class: "form-label" }),
              { class: "col-auto" }
            ),

        markup("div", element, { class: multi ? "col-12" : "col-9" }),
      ],
      { class: "row g-2 d-flex justify-content-between mb-1" }
    );

    if (multi) {
      return markup("div", [container, { tag: "div", class: "add-btn" }]);
    }

    return container;
  },

  getComponentOutputElement: function (output) {
    const extractObject = (obj) => {
      const { markup } = utils;
      const { label, key: obj_key, type, data } = obj;
      const container = markup(
        "div",
        [
          {
            tag: "span",
            content: label,
            class: ["tag", `tag-${type}`].join(" "),
          },
        ],
        { class: "output-value" }
      );
      if (type === "object" && data) {
        for (const data_key in data) {
          const obj = data[data_key];
          container.append(extractObject(obj));
        }
      }
      return container;
    };
    const { markup } = utils;
    const { label, key, data_type, data } = output;
    const container = markup("div", "", { id: key, class: "" });
    container.append(
      extractObject({
        label: label,
        key: key,
        type: data_type,
        data: data,
      })
    );

    return container;
  },
  renderComponentSidePanel: function (component) {
    const { markup } = utils;
    const _ = workflow_components;
    _.sidePanel.open();

    const body = _.sidePanel.find("section");
    const header = _.sidePanel.find("header");
    const footer = _.sidePanel.find("footer");
    header.html("Component edition");
    body.empty();

    const { id, name } = component;
    const { inputs, outputs } = component.config;
    const inputArray = inputs || [];
    const outputArray = outputs || [];

    const template = document.querySelector("#component-side-panel-template");
    const templateSettings = document.querySelector(
      "#component-setting-side-panel-template"
    );
    const clone = template.content.cloneNode(true);
    const cloneSettings = templateSettings.content.cloneNode(true);
    const elementId = `node_panel_${id}`;
    clone.querySelector(".component-side-node").setAttribute("id", elementId);
    clone
      .querySelector(".component-side-node")
      .setAttribute("data-component-id", id);

    body.append(cloneSettings);
    // Settings setup
    $(`#component-settings-form`).find(".component-name").val(name);
    // $(`#component-settings-form`).find("button").hide();
    _.addComponentSettingsFunctionality(component);
    // End Settings setup

    body.append(clone);
    body.append(
      markup(
        "div",
        [
          {
            tag: "textarea",
            class: "editor",
            name: "editor",
            style: "display: none",
          },
        ],
        { class: "panel-value-edition" }
      )
    );

    $(`#${elementId}`).find(".component-label").html(name);
    $(`#${elementId}`).find(".card-header i").first()?.attr("class", component.ui?.class_name ?? "bi bi-gear");
    for (let i = 0; i < inputArray.length; i++) {
      const input = inputArray[i];
      const divElementId = `${elementId}_${input.key}`;
      const inputElement = _.getComponentInputElement({
        ...input,
        elementId: divElementId,
      });
      $(`#${elementId}`).find(".list-group.input").append(inputElement);

      $(
        `#${divElementId}.input-value, #${divElementId}_array .input-value`
      ).valueSelector({
        input: input,
        component: component,
        isEdition: _.is_edition,
        portal: $(body).find(".panel-value-edition"),
      });
    }
    if (outputArray.length > 0) {
      $(`#${elementId}`).find(".list-group.output").show();
    }
    for (let i = 0; i < outputArray.length; i++) {
      const output = outputArray[i];
      const divElementId = `${elementId}_${output.key}`;
      const outputElement = _.getComponentOutputElement({
        ...output,
      });
      $(`#${elementId}`).find(".list-group.output").append(outputElement);
    }

    _.addMenuButtonsFunctionality(elementId, component);
  },
  api: {
    addComponent: function (data, success_callback, error_callback) {
      const _ = workflow_components;
      const component_route = data.route;

      return new Promise((resolve, reject) => {
        $.ajax({
          url: _.var.base_url,
          type: "POST",
          headers: { "X-CSRFToken": $("#csrf_token").val() },
          contentType: "application/json",
          data: JSON.stringify({
            ...data,
            workflow_id: _.workflow_id,
            version_id: _.version_id,
          }),
          success: function (data) {
            _.var.components.push(data);
            $(".main-add-component").hide();
            const after = component_route
              ? $(`#node_${component_route}`)
              : null;
            _.appendComponent(data, after);
            $(".component-node, .diagram-node-parent").draggable({});
            if (_.var.components.length === 1) {
              _.renderFirstLine(data);
            }
            _.renderRouteLine(data);
            if (component_route) {
              const source_component = _.var.components.find(
                (component) => component.id === component_route
              );
              if (source_component) {
                source_component.conditions.route = data.id;
                _.renderRouteLine(source_component);
              }
            }
            _.updateLines();
            $(`#node_${data.id}`).find(".btn-dropdown").trigger("click");
            resolve(data);
          },
          error: function (error) {
            reject(error);
          },
        });
      });
    },
    updateComponent: function (data, success_callback, error_callback) {
      const _ = workflow_components;
      $.ajax({
        url: _.var.base_url + data.id + "/update_component/",
        type: "PUT",
        headers: { "X-CSRFToken": $("#csrf_token").val() },
        contentType: "application/json",
        data: JSON.stringify({
          ...data,
          workflow_id: _.workflow_id,
          version_id: _.version_id,
        }),
        success: success_callback,
        error: error_callback,
      });
    },
    refreshComponentData: function (data, success_callback, error_callback) {
      const _ = workflow_components;
      const params = {
        workflow_id: _.workflow_id,
        version_id: _.version_id,
      };
      const queryParams = utils.make_query_params(params);
      $.ajax({
        url: _.var.base_url + data.id + "/?" + queryParams,
        type: "GET",
        headers: { "X-CSRFToken": $("#csrf_token").val() },
        contentType: "application/json",
        data: JSON.stringify({
          ...data,
          workflow_id: _.workflow_id,
          version_id: _.version_id,
        }),
        success: success_callback,
        error: error_callback,
      });
    },
    updateComponentInputValue: function (data) {
      const _ = workflow_components;
      return new Promise((resolve, reject) => {
        $.ajax({
          url: _.var.base_url + data.component_id + "/update_input_value/",
          type: "PUT",
          headers: { "X-CSRFToken": $("#csrf_token").val() },
          contentType: "application/json",
          data: JSON.stringify({
            ...data,
            workflow_id: _.workflow_id,
            version_id: _.version_id,
          }),
          success: function (response) {
            resolve(response);
          },
          error: function (error) {
            reject(error);
          },
        });
      });
    },
    deleteComponent: function (data, success_callback, error_callback) {
      const _ = workflow_components;
      const { id, workflow_id } = data;
      const _params = {
        workflow_id: workflow_id,
        version_id: _.version_id,
      };
      const queryParams = utils.make_query_params(_params);

      $.ajax({
        url: _.var.base_url + id + "/?" + queryParams,
        type: "DELETE",
        headers: { "X-CSRFToken": $("#csrf_token").val() },
        contentType: "application/json",
        success: success_callback,
        error: error_callback,
      });
    },
  },

  fetchPluginDefinitions: function () {
    const promise = new Promise((resolve, reject) => {
      const _ = workflow_components;
      $.ajax({
        // url: "/bwf/api/component-definitions/",
        url: "/bwf/api/plugin-definitions/",
        type: "GET",
        success: function (data) {
          _.pluginDefinitions = data;
          resolve(data);
        },
        error: function (error) {
          console.error(error);
          reject(error);
        },
      });
    });
    return promise;
  },

  updateInputValue: function (componentId, key, value, json_value) {
    const _ = workflow_components;
    const component = _.var.components.find(
      (component) => component.id === componentId
    );
    // const input = component.config.inputs.find((input) => input.key === key);
    // input.value = value;
    // input.json_value = json_value;
  },
  removeComponent: function (id) {
    const _ = workflow_components;
    const components = _.var.components;
    const index = _.var.components.findIndex(
      (component) => component.id === id
    );
    if (index === -1) {
      return;
    }
    const component = components[index];
    if (component && component.diagram) {
      component.diagram.line_out?.remove();
      component.diagram.line_in?.remove();
    }
    $(`#node_${component.id}`).off("drag.line_out");
    $(`#node_${component.id}`).off("drag.line_in");
    const nextComponent = components.find(
      (c) => c.id === component.conditions.route
    );
    const prevComponent = components.find(
      (c) => c.conditions.route === component.id
    );
    if (prevComponent) {
      prevComponent.conditions.route = nextComponent ? nextComponent.id : null;
      if (prevComponent.diagram?.line_out) {
        prevComponent.diagram.line_out = null;
        $(`#node_${prevComponent.id}`).off("drag.line_out");
        if (prevComponent.diagram.line_in) {
          $(`#node_${prevComponent.id}`).on(
            "drag.line_in",
            { isSource: false, id: prevComponent.id },
            _.handleLineDrag
          );
        }
      }
      if (prevComponent.conditions.route) {
        _.renderRouteLine(prevComponent);
      }
    }
    if (nextComponent) {
      if (nextComponent.diagram?.line_out) {
        // nextComponent.diagram.line_out = null;
        $(`#node_${nextComponent.id}`).off("drag.line_out");
        if (nextComponent.diagram.line_out) {
          $(`#node_${nextComponent.id}`).on(
            "drag.line_out",
            { isSource: true, id: nextComponent.id },
            _.handleLineDrag
          );
        }
      }
    }

    components.splice(index, 1);
    _.updateLines();

    if (components.length === 0) {
      $(".main-add-component").show();
      _.firstLine.remove();
    }
  },
  updateLines: function () {
    const _ = workflow_components;
    _.var.components.forEach((component) => {
      if (component.diagram?.line_in) {
        component.diagram.line_in.position();
      }
      if (component.diagram?.line_out) {
        component.diagram.line_out.position();
      }
    });
  },
};
