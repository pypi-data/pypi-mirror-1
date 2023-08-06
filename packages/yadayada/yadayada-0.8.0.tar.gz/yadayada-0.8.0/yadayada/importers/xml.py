from lxml import etree
from yadayada.utils.functional import list_to_dict
from django.core.serializers.python import Deserializer
from django.db import connection
from django.db import transaction
from django.db import models


class ElementHandler(object):

    def __init__(self, model, pk, **kwargs):
        self.model = model
        self.pk_field_name = pk
        self.related_to = kwargs.get("rel", dict())
        self.foreign_keys = kwargs.get("fkey", dict())
        # Always remove the primary key field that we change to django pk's.
        # Same with any foreign keys
        self.ignore_fields = list_to_dict(
                self.pk_field_name,
                [fkey[0] for fkey in self.foreign_keys], # fkey_pk_field
                kwargs.get("ignore_fields", list()))

    def is_wanted_field(self, field):
        """ Returns True if the field is a field wanted in the
        Django model.  """
        if field not in self.ignore_fields:
            return True

    def clean_data(self, data):
        cleansed = [(field, data) for field, data in data.items()
                                  if self.is_wanted_field(field)]
        return dict(cleansed)

    def deserialize(self, model, pk, fields, **options):
        object_list = [{"model": model, "pk": pk, "fields": fields}]
        return Deserializer(object_list, **options)

    def process(self, data, importer=None, **options):
        model = self.model
        meta = model._meta
        model_name = ".".join([meta.app_label, meta.module_name])

        # Set primary key
        pk = data.get(self.pk_field_name)

        # Fetch and connect foreign keys
        for fk_pk_field, fk_model, fk_attr in self.foreign_keys:
            data[fk_attr] = data[fk_pk_field]

        fields = self.clean_data(data)

        for field, value in fields.items():
            if isinstance(meta.get_field(field), models.BooleanField):
                fields[field] = bool(value)

        objects = self.deserialize(
                model=model_name, pk=pk, fields=fields,
                **options)
        [object.save() for object in objects]
        return objects


class RelationElementHandler(ElementHandler):

    def __init__(self, obj_model, obj_pk, rel_model, rel_pk, rel_manager):
        self.obj_model = obj_model
        self.obj_pk_name = obj_pk
        self.rel_model = rel_model
        self.rel_pk_name = rel_pk
        self.rel_manager_name = rel_manager

    def process(self, data, importer=None, **options):
        # Get primary keys
        rel_pk = data[self.rel_pk_name]
        obj_pk = data[self.obj_pk_name]

        # Fetch the objects
        obj = self.obj_model.objects.get(pk=obj_pk)
        rel = self.rel_model(pk=rel_pk)

        # Get the relation manager
        obj_rel_manager = getattr(obj, self.rel_manager_name)

        # Connect the objects
        obj_rel_manager.add(rel)


class XPathImporter(object):

    parser = etree.parse
    xpath_prefix = "/"

    def __init__(self, *args, **options):
        self.document = self.open_document(*args)
        self.options = options

    def open_document(self, *args):
        return self.parser(*args)

    def import_to_django(self):
        if not hasattr(self, "handlers"):
            raise AttributeError(
                "XPathImporter classes must have handlers defined")

        cursor = connection.cursor()
        commit = self.options.get("commit", True)
        if commit:
            transaction.commit_unless_managed()
            transaction.enter_transaction_management()
            transaction.managed(True)

        try:
            [self.run_handler(tag, handler)
                for tag, handler in self.handlers]
            if commit:
                transaction.commit()
        except Exception, e:
            objs = []
            transaction.rollback()
            transaction.leave_transaction_management()
            raise

    def run_handler(self, tag, handler):
        return [handler.process(data, self, **self.options)
                    for data in self.iternodes(tag)]

    def iternodes(self, node_name):
        xpath_expr = "/".join((self.xpath_prefix, node_name))
        app_nodes = self.document.xpath(xpath_expr)
        for app_node in app_nodes:
            yield self.node_to_dict(app_node)

    def node_to_dict(self, element):
        return dict([(child.tag, child.text)
            for child in element.iterdescendants()])
