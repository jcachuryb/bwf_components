var workflow_components = {
  workflow_id: null,
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

  init: function (workflow_id, containerId) {
    const _ = workflow_components;
    if (!workflow_id || !containerId) {
      console.error("workflow_id and containerId are required");
      console.error("workflow_id is required");
      return;
    }
    _.workflow_id = workflow_id;
    _.containerId = containerId;
    _.container = $(`#${containerId}`);
    // Add + Buttton
    const _params = {
      workflow_id: _.workflow_id,
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
    for (let i = 0; i < components.length; i++) {
      const component = components[i];
      _.appendComponent(component);
      $(".component-node").draggable({});
    }
    for (let i = 0; i < components.length; i++) {
      const component = components[i];
      if (component.conditions.route) {
        console.log("route", component.conditions.route);
        const route = component.conditions.route;
        const start = $(`#node_${component.id}`);
        const end = $(`#node_${route}`);
        const line = new LeaderLine(start[0], end[0], {
          color: "#0d6efd",
          size: 2,
          middleLabel: "Route",
        });
        $(`#node_${component.id}, #node_${route}`).on(
          "drag",
          function (event, ui) {
            line.position();
          }
        );
      }
    }
  },
  appendComponent: function (component) {
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

    _.container.append(clone);
    $(`#${elementId}`).find(".component-label").html(name);
    for (let i = 0; i < inputArray.length; i++) {
      const input = inputArray[i];
      const divElementId = `${elementId}_${input.key}`;
      const inputElement = _.getComponentInputElement({
        ...input,
        elementId: divElementId,
      });
      $(`#${elementId}`).find(".list-group.input").append(inputElement);

      $(`#${divElementId}.input-value`).valueSelector({
        input: input,
        component: component,
      });
    }
    if(outputArray.length >  0){
      $(`#${elementId}`).find(".list-group.output").show() 
    }
    for (let i = 0; i < outputArray.length; i++) {
      const output = outputArray[i];
      const divElementId = `${elementId}_${output.key}`;
      const inputElement = _.getComponentOutputElement({
        ...output
      });
      $(`#${elementId}`).find(".list-group.output").append(inputElement);

    }

    // Delete Component
    $(`#${elementId}`)
      .find(".delete-component")
      .on("click", component, function (event) {
        const _ = workflow_components;
        const { id } = event.data;
        const data = { id: id, workflow_id: _.workflow_id };
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
        console.log({component});
      });
  },
  getComponentInputElement: function (input) {
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

    // if (value_rules && value_rules.variable_only) {
    //   element = markup(
    //     "select",
    //     [
    //       markup("option", "Select Variable", { value: "" }),
    //       workflow_variables.var.variables.map((variable) => {
    //         return markup("option", variable.label, { value: variable.key });
    //       }),
    //     ],
    //     {
    //       id: elementId,
    //       name: key,
    //       class: "form-select form-select-sm",
    //     }
    //   );
    // }

    // if (data_type === "string") {
    //   element = markup("input", null, {
    //     type: "text",
    //     class: "form-control form-control-sm",
    //     id: elementId,
    //     name: key,
    //     value: default_value,
    //   });
    // } else if (data_type === "number") {
    //   element = markup("input", null, {
    //     type: "number",
    //     class: "form-control form-control-sm",
    //     id: elementId,
    //     name: key,
    //     value: default_value,
    //   });
    // } else if (data_type === "boolean") {
    //   element = markup("input", null, {
    //     type: "checkbox",
    //     class: "form-check-input",
    //     id: elementId,
    //     name: key,
    //     value: default_value,
    //   });
    // } else if (data_type === "array") {
    //   element = markup("input", null, {
    //     type: "text",
    //     class: "form-control form-control-sm",
    //     id: elementId,
    //     name: key,
    //     value: default_value,
    //   });
    // } else if (data_type === "object") {
    //   element = markup("input", null, {
    //     type: "text",
    //     class: "form-control form-control-sm",
    //     id: elementId,
    //     name: key,
    //     value: default_value,
    //   });

    // }

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
          data: JSON.stringify({ ...data, workflow_id: _.workflow_id }),
          success: function (data) {
            _.var.components.push(data);
            _.appendComponent(data);
            if (component_route) {
              const source_component = _.var.components.find(
                (component) => component.id === component_route
              );
              if (source_component) {
                source_component.conditions.route = data.id;
              }
            }
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
        data: JSON.stringify({ ...data, workflow_id: _.workflow_id }),
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
        data: JSON.stringify({ ...data, workflow_id: _.workflow_id }),
        success: success_callback,
        error: error_callback,
      });
    },
    deleteComponent: function (data, success_callback, error_callback) {
      const _ = workflow_components;
      const { id, workflow_id } = data;
      const _params = {
        workflow_id: workflow_id,
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
    const index = _.var.components.findIndex(
      (component) => component.id === id
    );
    if (index === -1) {
      return;
    }
    _.var.components.splice(index, 1);
  },
};
