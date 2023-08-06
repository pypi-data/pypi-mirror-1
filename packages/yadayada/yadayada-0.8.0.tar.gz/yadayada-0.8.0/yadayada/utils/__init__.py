import os


def template_path_builder(app_name, suffix="html"):
    suffix = suffix.startswith(".") and suffix or "." + suffix
    return lambda template: os.path.join(app_name, template) + suffix
