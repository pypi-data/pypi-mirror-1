from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template import Library, Node

register = Library()

@register.tag
def content_type_id(parser, token):
    """
    Returns the content type id for the model given by its app_label and its
    model_name.
    """
    app_label, model_name = token.split_contents()[1:]
    return ContentTypeIdNode(app_label, model_name)


class ContentTypeIdNode(Node):
    def __init__(self, app_label, model_name):
        self.app_label = app_label
        self.model_name = model_name
    
    def render(self, context):
        model = models.get_model(self.app_label, self.model_name)
        if not model:
            raise Exception('Check app_label and model_name in template tag!')
        return ContentType.objects.get_for_model(model).id

