from pathlib import Path

from jinja2 import Environment, FileSystemLoader

path = Path(__file__).parent / "prompt_templates"

loader = FileSystemLoader(path)
env = Environment(loader=loader)


def render(template_name: str, **kwargs: str) -> str:
    template = env.get_template(template_name)
    return template.render(**kwargs)
