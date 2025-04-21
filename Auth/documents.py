from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import User



@registry.register_document
class UserDocument(Document):
    
    class Index:
        # Name of the Elasticsearch index
        name = 'user'
        # Optional settings for the index
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }

    class Django:
        model = User
        fields = [
            'name',
            'email',
            'type',
        ]

