var workflow_inputs = {
    workflow_id: null,
    add_input_btn: null,
    containerId: null,
    container: null,

    selectedInput: null,
    progressBar: null,
    progressContainer: null,
    inputsController: null,
    variablesController: null,
    componentsController: null,
    var: {
      base_url: "/bwf/api/workflow-inputs/",
      inputs: []
    },
  
    init: function (workflow_id, containerId) {
      const _ = workflow_inputs
      if(!workflow_id || !containerId){
        console.error("workflow_id and containerId are required")
        console.error("workflow_id is required")
        return
      }
      _.workflow_id = workflow_id
      _.containerId = containerId
      _.container = $(`#${containerId} #inputs`)
      _.add_input_btn = $(`#${containerId} button.add-input`)
      // Add + Buttton
      const _params = {
        workflow_id: _.workflow_id
      };
      const queryParams = utils.make_query_params(_params);
      $.ajax({
        url: _.var.base_url + "?" + queryParams,
        type: "GET",
        success: function (data) {
          _.var.inputs = data;
          _.renderInputs();
        },
        error: function (error) {
          console.error(error);
        },
      });

      _.add_input_btn.on("click", function () {
        const _ = workflow_inputs
        _.selectedInput = null
        $('#inputs-modal').modal('show')
      })
    },
    renderInputs: function () {
      const _ = workflow_inputs
      const inputs = _.var.inputs
      for (let i = 0; i < inputs.length; i++) {
        const input = inputs[i]
        _.appendInput(input)
      }
    },
    appendInput: function (input) {
      const _ = workflow_inputs
      const elementId = `input_${input.id}`
      const inputMarkup = `
          <label id="${elementId}" class="list-group-item d-flex gap-1">
            <div class="d-flex gap-2 justify-content-between w-100">
            <span>
              ${input.label}
              <small class="d-block text-body-secondary">${input.description}</small>
              <span class="badge rounded-pill text-bg-info">${input.data_type}</span>
            </span>
            <div class="form-check form-switch">
              <button class="btn btn-ghost add-input"data-input-id="${input.id}">
                <i class="bi bi-gear"></i>
              </button>
              <button class="btn btn-ghost remove-input" data-input-id="${input.id}">
                <i class="bi bi-trash text-danger"></i>
              </button>
            </div>
            </div>
          </label>
        `
        _.container.append(inputMarkup)
        $(`#${elementId} button.add-input`).on("click", function () {
          const _ = workflow_inputs
          _.selectedInput = input
          $('#inputs-modal').modal('show')
        })
        $(`#${elementId} button.remove-input`).on("click", function () {
          const _ = workflow_inputs
          _.selectedInput = input
          console.log('remove',input)
        })
    },
    api: {

      addInput: function (input, success_callback, error_callback) {
        const _ = workflow_inputs
        $.ajax({
          url: _.var.base_url,
          type: "POST",
          headers: {'X-CSRFToken' : $("#csrf_token").val()},
          contentType: "application/json",
          data: JSON.stringify({...input, workflow_id: _.workflow_id}),
          success: success_callback,
          error: error_callback,
        });
      },
      updateInput: function (input, success_callback, error_callback) {
        const _ = workflow_inputs
        $.ajax({
          url: _.var.base_url + input.id + "/",
          type: "PUT",
          headers: {'X-CSRFToken' : $("#csrf_token").val()},
          contentType: "application/json",
          data: JSON.stringify({...input, workflow_id: _.workflow_id}),
          success: success_callback,
          error: error_callback,
        });
      },
      deleteInput: function (input, success_callback, error_callback) {
        const _ = workflow_inputs
        $.ajax({
          url: _.var.base_url + input.id + "/?workflow_id=" + _.workflow_id,
          type: "DELETE",
          headers: {'X-CSRFToken' : $("#csrf_token").val()},
          contentType: "application/json",
          success: success_callback,
          error: error_callback,
        });
      },
    }
     
    

  };
  