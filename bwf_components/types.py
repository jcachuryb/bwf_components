from abc import ABC, abstractmethod

class AbstractPluginHandler(ABC):
    """
    Abstract base class for plugin handlers.
    """

    @abstractmethod
    def collect_context_data(self) -> dict:
        """
        Collect context data for the plugin.
        """
        pass
    @abstractmethod
    def set_output(self, success: bool, data: dict=None, message: str = None):
        """
        Set the output for the plugin.
        """
        pass

    @abstractmethod
    def update_workflow_variable(self, id:str, value):
        """
        Update the workflow variable with the given id and value.
        """
        pass