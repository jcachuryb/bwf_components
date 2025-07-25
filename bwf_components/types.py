from abc import ABC, abstractmethod


class AbstractPluginHandler(ABC):
    """
    Abstract base class for plugin handlers.
    """

    @abstractmethod
    def workflow_instance_id(self) -> int:
        """
        Get the workflow instance ID.
        """
        pass

    @abstractmethod
    def component_instance_id(self) -> int:
        """
        Get the component instance ID.
        """
        pass

    @abstractmethod
    def collect_context_data(self) -> dict:
        """
        Collect context data for the plugin.
        """
        pass

    @abstractmethod
    def set_output(self, success: bool, data: dict = None, message: str = None):
        """
        Set the output for the plugin.
        """
        pass

    @abstractmethod
    def update_workflow_variable(self, id: str, value):
        """
        Update the workflow variable with the given id and value.
        """
        pass

    @abstractmethod
    def set_on_awaiting_action(self):
        """
        Set the component instance to awaiting action state.
        """
        pass
