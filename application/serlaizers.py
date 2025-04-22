from rest_framework import serializers
from . import models
from Auth import serlaizers as sr
from post import serializer as psr
from Auth import tasks
class application_serializer(serializers.ModelSerializer):
    team=psr.team_serializer(read_only=True,many=False)
    proposal=serializers.CharField(required=True)
    status=serializers.CharField(read_only=True)
    attechment=serializers.FileField(required=False)
    class Meta:
        model = models.Application
        fields = ['id','title','team','proposal','status','atachedfile','attechment','links']
    def create(self, validated_data):
        if 'attechment' in validated_data:
            validated_data['atachedfile']= tasks.upload_to_supabase(validated_data.pop('attechment'),validated_data['team'].name)
        application = models.Application.objects.create(**validated_data)
        return application
    def update(self, instance, validated_data):
        if 'attechment' in validated_data:
            validated_data['atachedfile']= tasks.upload_to_supabase(validated_data.pop('attechment'),instance.team.name)
        instance = super().update(instance, validated_data)
        return instance