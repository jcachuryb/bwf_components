var workflow_components = {
  workflow_id: null,
  add_component_btn: null,
  containerId: null,
  container: null,

  selectedComponent: null,
  var: {
    base_url: "/bwf/api/workflow-components/",
    csrf_token: null,
    components: [],
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
  },
  renderComponents: function () {
    const _ = workflow_components;
    const components = _.var.components;
    // if (components.length === 0) $(".main-add-component").show();
    // if (components.length > 0) $(".main-add-component").hide();
    for (let i = 0; i < components.length; i++) {
      const component = components[i];
      _.appendComponent(component);
    }
  },
  appendComponent: function (component) {
    const template = document.querySelector("#component-node-template");
    const { markup } = utils;

    const { id, name, input, output } = component;
    const inputArray = input || [];
    const outputArray = output || [];
    // Clone the new row and insert it into the table
    const clone = template.content.cloneNode(true);
    const _ = workflow_components;
    const elementId = `node_${id}`;
    clone.querySelector(".component-node").setAttribute("id", elementId);
    _.container.append(clone);
    $(`#${elementId}`).find(".component-label").html(name);
    const inputElement = markup("div");
    for (let i = 0; i < inputArray.length; i++) {
      const input = inputArray[i];
      const inputElement = _.getComponentInputElement(input);
      $(`#${elementId}`).find(".list-group.input").append(inputElement);
      $(`#${input.id}`)
    }
    
    // $(`#${elementId}`).find(".list-group.output").html("<h4> Output </h4>");
    // $(`#${elementId}`).find(".list-group.on-fail").html("<h4> On Fail </h4>");
  },
  getComponentInputElement: function (input) {
    const { markup } = utils;
    const {
      id,
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

    let element = null;
    if (data_type === "string") {
      element = markup("input", null, {
        type: "text",
        class: "form-control form-control-sm",
        id: key,
        name: key,
        value: default_value,
      });
    } else if (data_type === "number") {
      element = markup("input", null, {
        type: "number",
        class: "form-control form-control-sm",
        id: key,
        name: key,
        value: default_value,
      });
    } else if (data_type === "boolean") {
      element = markup("input", null, {
        type: "checkbox",
        class: "form-check-input",
        id: key,
        name: key,
        value: default_value,
      });
    } else if (data_type === "array") {
      element = markup("input", null, {
        type: "text",
        class: "form-control form-control-sm",
        id: key,
        name: key,
        value: default_value,
      });
    } else if (data_type === "object") {
      element = markup("input", null, {
        type: "text",
        class: "form-control form-control-sm",
        id: key,
        name: key,
        value: default_value,
      });
    
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
            element,
          { class: "col-auto" }
        ),
      ],
      { class: "row g-3 d-flex justify-content-between mb-1" }
    );

    return container;
  },
  api: {
    addComponent: function (data, success_callback, error_callback) {
      const _ = workflow_components;

      return new Promise((resolve, reject) => {
        $.ajax({
          url: _.var.base_url,
          type: "POST",
          headers: { "X-CSRFToken": _.csrf_token },
          contentType: "application/json",
          data: JSON.stringify({ ...data, workflow_id: _.workflow_id }),
          success: function (data) {
            _.appendComponent(data);
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
        headers: { "X-CSRFToken": _.csrf_token },
        contentType: "application/json",
        data: JSON.stringify({ ...data, workflow_id: _.workflow_id }),
        success: success_callback,
        error: error_callback,
      });
    },
    deleteComponent: function (data, success_callback, error_callback) {
      const _ = workflow_components;
      $.ajax({
        url: _.var.base_url + data.id + "/",
        type: "DELETE",
        headers: { "X-CSRFToken": _.csrf_token },
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
};
