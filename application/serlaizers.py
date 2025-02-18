from rest_framework import serializers
from . import models
from Auth import serlaizers as sr
from post import serializer as psr
class application_serializer(serializers.ModelSerializer):
    team=psr.team_serializer(required=False,many=False)
    class Meta:
        model = models.Application
        fields = ['id','team','proposal','status','approve']