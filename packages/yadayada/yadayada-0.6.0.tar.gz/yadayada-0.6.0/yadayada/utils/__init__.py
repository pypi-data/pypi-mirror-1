import os


def template_path_builder(app_name):
    return lambda template: os.path.join(app_name, template) + ".html"
