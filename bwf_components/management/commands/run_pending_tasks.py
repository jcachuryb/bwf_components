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
logger = logging.getLogger(__name__)


class Command(base.BaseCommand):
    """Run Pending Tasks Command."""
    # Help string
    help = "Processes Spatial Layers Monitor"  # noqa: A003

    def handle(self, *args, **kwargs) -> None:
        """Handles the management command functionality."""
        # Display information
        self.stdout.write("Processing pending components...")
        ProcessPendingComponents().run()

        
        

