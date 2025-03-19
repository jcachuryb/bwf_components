var workflow_components = {
  workflow_id: null,
  version_id: null,
  is_edition: true,
  has_init: false,
  add_component_btn: null,
  containerId: null,
  container: null,

  selectedComponent: null,
  var: {
    base_url: "/bwf/api/workflow-components/",
    components: [],
    definitions: [],
    incoming: [],
  },
  pluginDefinitions: [],

  init: function (options, containerId) {
    const { workflow_id, version_id, is_edition } = options;
    const _ = workflow_components;
    if (!workflow_id || !version_id || !containerId) {
      console.error("workflow_id and containerId are required");
      console.error("workflow_id is required");
      return;
    }
    _.workflow_id = workflow_id;
    _.version_id = version_id;
    _.containerId = containerId;
    _.container = $(`#${containerId}`);
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
        $(".component-node").draggable({});

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
      _.renderRouteLine(component);
    }
    const container = $("body");

    var scrollTo = $("#components-flow");
    var position =
      scrollTo.offset().top - container.offset().top + container.scrollTop();
    container.scrollTop(position);
  },
  renderRouteLine: function (component) {
    const _ = workflow_components;
    if (component.conditions.route) {
      const route = component.conditions.route;
      const start = $(`#node_${component.id}`);
      const end = $(`#node_${route}`);
      if (start.length > 0 && end.length > 0) {
        const components = _.var.components;
        const destination = components.find(
          (component) => component.id === route
        );

        try {
          destination.diagram?.line_in?.remove();
        } catch (error) {}

        const line = new LeaderLine(start[0], end[0], {
          color: "#0d6efd",
          size: 2,
          middleLabel: `${component.name} -> ${destination.name}`,
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
  appendComponent: function (component, appendAfter) {
    const template = document.querySelector("#component-node-template");
    const { markup } = utils;

    const { id, name } = component;
    const { inputs, outputs } = component.config;
    const inputArray = inputs || [];
    const outputArray = outputs || [];
    // Clone the new row and insert it into the table
    const clone = template.content.cloneNode(true);
    const _ = workflow_components;
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
      });
    }
    if (outputArray.length > 0) {
      $(`#${elementId}`).find(".list-group.output").show();
    }
    for (let i = 0; i < outputArray.length; i++) {
      const output = outputArray[i];
      const divElementId = `${elementId}_${output.key}`;
      const inputElement = _.getComponentOutputElement({
        ...output,
      });
      $(`#${elementId}`).find(".list-group.output").append(inputElement);
    }

    // Delete Component
    $(`#${elementId}`)
      .find(".delete-component")
      .on("click", component, function (event) {
        const _ = workflow_components;
        const { id } = event.data;
        const data = {
          id: id,
          workflow_id: _.workflow_id,
          version_id: _.version_id,
        };
        _.api.deleteComponent(data, function (data) {
          $(`#${elementId}`).remove();
          workflow_components.removeComponent(id);
        });
      });
    // END: Delete Component

    $(`#${elementId}`)
      .find(".print-component")
      .on("click", component, function (event) {
        const _ = workflow_components;
        const { id } = event.data;
        const component = _.var.components.find(
          (component) => component.id === id
        );
        console.log({ component });
      });
    $(`#${elementId}`)
      .find(".add-next-component")
      .on("click", component, function (event) {
        new_component_data.selectedComponent.data = event.data;
        $("#component-creation-modal").modal("show");
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
    const structure = json_value?.structure;

    let element = markup("div", "", {
      id: elementId,
      name: key,
      class: "input-value",
    });

    if (multi) {
      if (structure) {
        const input_structures = [];
        for (const structure_key in structure) {
          const structure_input = structure[structure_key];
          const divElementId = `${elementId}_${structure_input.key}`;
          const inputElement = _.getComponentInputElement({
            ...structure_input,
            elementId: `${elementId}_${structure_input.key}`,
          });
          input_structures.push(inputElement);
        }

        const container = markup(
          "div",
          [
            markup(
              "div",
              markup("label", name, { for: key, class: "form-label" }),
              { class: "col-auto" }
            ),

            markup(
              "div",
              markup("div", input_structures, { id: `${elementId}_array` }),
              {
                class: "col-12",
              }
            ),
          ],
          { id: elementId, class: "row g-2  justify-content-between mb-1" }
        );

        return container;
      }
    }
    const container = markup(
      "div",
      [
        markup(
          "div",
          markup("label", name, { for: key, class: "form-label" }),
          { class: "col-auto" }
        ),

        markup("div", element, { class: "col-9" }),
      ],
      { class: "row g-2 d-flex justify-content-between mb-1" }
    );

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
    const { name, key, data_type, data } = output;
    const container = markup("div", "", { id: key, class: "" });
    container.append(
      extractObject({
        label: name,
        key: key,
        type: data_type,
        data: data,
      })
    );

    return container;
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
            const after = component_route
              ? $(`#node_${component_route}`)
              : null;
            _.appendComponent(data, after);
            $(".component-node").draggable({});
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
        url: _.var.base_url + data.id + "/",
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
    updateComponentInputValue: function (
      data,
      success_callback,
      error_callback
    ) {
      const _ = workflow_components;
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
        success: success_callback,
        error: error_callback,
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
    const input = component.config.inputs.find((input) => input.key === key);
    input.value = value;
    input.json_value = json_value;
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
