from pathlib import Path
from typing import Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape


class EmailTemplateService:
    """Load and render HTML email templates located under `app/templates/emails`.

    Templates are classic Jinja2 HTML files. Use `render(template_name, context)`
    to get the final HTML string.
    """

    def __init__(self, templates_dir: Optional[str] = None):
        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            self.templates_dir = Path(__file__).resolve().parents[1] / "templates" / "emails"

        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render(self, template_name: str, context: Dict = None) -> str:
        tmpl = self.env.get_template(template_name)
        return tmpl.render(**(context or {}))
