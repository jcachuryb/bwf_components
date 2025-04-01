var component_utils = {
  findComponentInTree: function (id, config) {
    const _ = workflow_components;
    const path = config?.path.split(".") || [];
    const parentId = path ? (path.length > 0 ? path[0] : id) : id;
    let component = _.var.components.find(
      (component) => component.id === parentId
    );
    if (!component) {
      console.error("Component not found", parentId);
      return;
    }
    for (let i = 1; i < path.length; i++) {
      const key = path[i];
      if(Array.isArray(component)) {
        component = component.find((comp) => comp.id === key);
      }else if (component[key]) {
        component = component[key];
      } else {
        console.error("Component not found", key);
        return;
      }
    }
    return component;
  },

  render: {
    renderBranch: function (elementId, component) {
      const _ = workflow_components;
      // draw branch
      const branch = component.config.branch;
      const branchTrue = branch.True;
      const branchFalse = branch.False;

      const branchTemplate = document.querySelector(
        "#component-branch-template"
      );
      const clone = branchTemplate.content.cloneNode(true);
      const branchElemId = `branch_${component.id}`;
      clone.querySelector("div").id = branchElemId;

      // $(`#node_${component.id}`).find('.component-dot-add').remove();
      $(`#${elementId} .component-label`).after(clone);
      $(`#${elementId} .branch-true .component-out`)
        .attr("data-parent-node-type", "branch")
        .attr("data-path", "True")
        .attr("data-parent-id", component.id)
        .attr("data-parent-node-path", component.config.path || "")
        .attr("data-previous-node", null);
      $(`#${elementId} .branch-false .component-out`)
        .attr("data-parent-node-type", "branch")
        .attr("data-path", "False")
        .attr("data-parent-id", component.id)
        .attr("data-parent-node-path", component.config.path || "")
        .attr("data-previous-node", null);

      // $(`#node_${component.id}`).find(".branch-true").html(branchTrue);
      const start = $(`#node_${component.id} .diagram-node`);
      const lines = [
        {
          start: start,
          end: $(`#${branchElemId} .branch-true .component-out i`),
          color: "#0d6efd",
          label: "True",
        },
        {
          start: start,
          end: $(`#${branchElemId} .branch-false .component-out i`),
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

      // draw insides

      _.renderComponents(
        $(`#${branchElemId} .branch-true .workflow`),
        branchTrue
      );
      _.renderComponents(
        $(`#${branchElemId} .branch-false .workflow`),
        branchFalse
      );
      $(`#${branchElemId} .branch-true .component-route.component-out:first,
        #${branchElemId} .branch-false .component-route.component-out:first`)      
      ?.on("click", component, function (event) {
        const { selectedComponent } = new_component_data;
        selectedComponent.data = null;
        selectedComponent.path = $(this).data("path");
        selectedComponent.parentId = $(this).data("parent-id");
        selectedComponent.parentNodeType = $(this).data("parent-node-type");
        selectedComponent.parentNodePath = $(this).data("parent-node-path");
        selectedComponent.isEntry = true;
        console.log({selectedComponent})

        $("#component-creation-modal").modal("show");
      });
    },
    
  },
};
