var bwf_workflow = {
    progressBar: null,
    progressContainer: null,
    inputsController: null,
    variablesController: null,
    componentsController: null,
    var: {
      workflow: null,
      components: [],
      variables: [],
      inputs: []
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

  };
  