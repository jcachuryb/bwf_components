"""Spatial Layer Monitor Management Command."""


# Third-Party
import os
import logging
import subprocess
from django.core.management import base
from datetime import datetime
# Local
from bwf_components.workflow.models import WorkFlowInstance, ComponentInstance
from bwf_components.pending_components import ProcessPendingComponents
from bwf_components.tasks import start_workflow
logger = logging.getLogger(__name__)


class Command(base.BaseCommand):
    """Run Pending Tasks Command."""
    # Help string
    help = "Processes Spatial Layers Monitor"  # noqa: A003

    def handle(self, *args, **kwargs) -> None:
        """Handles the management command functionality."""
        # Display information
        self.stdout.write("Processing pending components...")
        # ProcessPendingComponents().run()
        start_workflow('1', {
                            "Input_1": {"key": "Input_1", "value": "hola mundo",},
                            "saludoMisPerritos": {"key": "saludoMisPerritos", "value": "Un saludo para el email",},
                            "otro_input": {"key": "otro_input", "value": "123",},
                            "has_registered": {"key": "has_registered", "value": True,},
                            "endpoint": {"key": "endpoint", "value": "http://localhost:9196/",},
        })

