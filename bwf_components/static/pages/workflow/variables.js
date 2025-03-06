var workflow_variables = {
    workflow_id: null,
    add_variable_btn: null,
    containerId: null,
    container: null,
    csrf_token: null,

    selectedVariable: null,
    progressBar: null,
    progressContainer: null,
    variablesController: null,
    variablesController: null,
    componentsController: null,
    var: {
      base_url: "/bwf/api/workflow-variables/",
      variables: []
    },
  
    init: function (workflow_id, containerId) {
      const _ = workflow_variables
      if(!workflow_id || !containerId){
        console.error("workflow_id and containerId are required")
        console.error("workflow_id is required")
        return
      }
      _.workflow_id = workflow_id
      _.containerId = containerId
      _.container = $(`#${containerId} #variables`)
      _.add_variable_btn = $(`#${containerId} button.add-variable`)
      // Add + Buttton
      const _params = {
        workflow_id: _.workflow_id
      };
      const queryParams = utils.make_query_params(_params);
      $.ajax({
        url: _.var.base_url + "?" + queryParams,
        type: "GET",
        success: function (data) {
          _.var.variables = data;
          _.renderVariables();
        },
        error: function (error) {
          console.error(error);
        },
      });

      _.add_variable_btn.on("click", function () {
        const _ = workflow_variables
        _.selectedVariable = null
        $('#variables-modal').modal('show')
      })
    },
    renderVariables: function () {
      const _ = workflow_variables
      const variables = _.var.variables
      for (let i = 0; i < variables.length; i++) {
        const variable = variables[i]
        _.appendVariable(variable)
      }
    },
    appendVariable: function (variable) {
      const _ = workflow_variables
      const elementId = `variable_${variable.id}`
      const variableMarkup = `
          <label id="${elementId}" class="list-group-item d-flex gap-2">
            <div class="d-flex gap-2 justify-content-between w-100">
            <span>
              ${variable.name}
              <small class="d-block text-body-secondary">${variable.data_type}</small>
            </span>
            <div class="form-check form-switch">
              <button class="btn btn-ghost edit-variable"data-variable-id="${variable.key}">
                <i class="bi bi-gear"></i>
              </button>
              <button class="btn btn-ghost remove-variable" data-variable-id="${variable.key}">
                <i class="bi bi-trash text-danger"></i>
              </button>
            </div>
            </div>
          </label>
        `
        _.container.append(variableMarkup)
        $(`#${elementId} button.edit-variable`).on("click", function (event) {
          const variableKey = $(event.currentTarget).data('variable-id')
          const _ = workflow_variables
          const variable = _.var.variables.find(v => v.key == variableKey)
          _.selectedVariable = variable
          $('#variables-modal').modal('show')
        })
        $(`#${elementId} button.remove-variable`).on("click", function () {
          const _ = workflow_variables
          _.selectedVariable = variable
          console.log('remove',variable)
        })
    },
    api: {

      addVariable: function (variable, success_callback, error_callback) {
        const _ = workflow_variables
        $.ajax({
          url: _.var.base_url,
          type: "POST",
          headers: {'X-CSRFToken' : $("#csrf_token").val() },
          contentType: "application/json",
          data: JSON.stringify({...variable, workflow_id: _.workflow_id}),
          success: success_callback,
          error: error_callback,
        });
      },
      updateVariable: function (variable, success_callback, error_callback) {
        const _ = workflow_variables
        $.ajax({
          url: _.var.base_url + variable.id + "/",
          type: "PUT",
          headers: {'X-CSRFToken' : $("#csrf_token").val() },
          contentType: "application/json",
          data: JSON.stringify({...variable, workflow_id: _.workflow_id}),
          success: success_callback,
          error: error_callback,
        });
      },
      deleteVariable: function (variable, success_callback, error_callback) {
        const _ = workflow_variables
        $.ajax({
          url: _.var.base_url + variable.id + "/",
          type: "DELETE",
          headers: {'X-CSRFToken' : $("#csrf_token").val() },
          contentType: "application/json",
          success: success_callback,
          error: error_callback,
        });
      },
    }
     
    

  };
  