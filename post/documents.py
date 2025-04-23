
from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import Opportunity

@registry.register_document
class OpportunityDocument(Document):
    
    class Index:
        
        name = 'opportunity'
       
        

    class Django:
        model = Opportunity
        fields = [
            'title',
            'description',
            'Type',
        ]

