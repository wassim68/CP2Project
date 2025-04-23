from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from post import models
from . import models as app_md
from Auth.models import User



@registry.register_document
class companyDocument(Document):
    class Index:
        name = 'company'

    class Django:
        model = User
        fields = ['name']

@registry.register_document
class Opportunitydocument(Document):
    class Index:
        name = 'opportunity'
    class Django:
        model = models.Opportunity
        fields = ['title']

@registry.register_document
class ApplicationDocument(Document):
    class Index:
        name = 'application'

    class Django:
        model = app_md.Application
        fields = ['title']
