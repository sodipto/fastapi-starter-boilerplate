from abc import ABC, abstractmethod
from typing import Dict, Optional


class IEmailTemplateService(ABC):
    """Interface for email template rendering services."""

    @abstractmethod
    def render(self, template_name: str, context: Optional[Dict] = None) -> str:
        """Render a template and return the HTML string.

        Args:
            template_name: Filename of the template under templates/emails.
            context: Mapping of template variables.
        Returns:
            Rendered HTML string.
        """
        raise NotImplementedError()
