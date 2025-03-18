var bwf_workflow = {
    progressBar: null,
    progressContainer: null,
    inputsController: null,
    variablesController: null,
    componentsController: null,
    var: {
      workflow: null,
      base_url: "/bwf/api/workflow/",
      components: [],
      variables: [],
      inputs: [],
    },
  
    init: function () {
      const _ = sam_dashboard;
      const params = new URL(document.location.toString()).searchParams;
  
      _.var.hasInit = false;
      _.var.page = Number(params.get("page")) || 1;
      _.var.page_size = Number(params.get("page_size")) || 10;
    //   _.enableSyncButton();
    //   _.renderDataTable();
    },

    api: {
      createWorkflow: function (data) {
        const _ = bwf_workflow;
        
        return new Promise((resolve, reject) => {
          $.ajax({
            url: _.var.base_url,
            type: "POST",
            headers: { "X-CSRFToken": $("#csrf_token").val() },
            contentType: "application/json",
            data: JSON.stringify({ ...data }),
            success: function (data) {
              window.location= `/bwf/workflow/${data.id}/edit`;
              resolve(data);
            },
            error: function (error) {
              alert("Error creating workflow");
              reject(error);
            },
          });
        });

      }
    }

  };
  