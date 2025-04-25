from django.db import models
from Auth.models import User



class Chat(models.Model):
    student = models.ForeignKey(User, related_name='chats_as_student', on_delete=models.DO_NOTHING)
    company = models.ForeignKey(User, related_name='chats_as_company', on_delete=models.DO_NOTHING)
    room_name = models.CharField(max_length=100, unique=True)
    last_message = models.OneToOneField('Message',related_name='last_chat',on_delete=models.DO_NOTHING,null=True)


    def save(self, *args, **kwargs):    
        self.room_name = f"room_{self.student.id}_{self.company.id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.room_name

    @classmethod
    def get_or_create_chat(cls, student, company):   
        chat, created = cls.objects.get_or_create(student=student, company=company)
        return chat

   

class Message(models.Model):
    sender = models.ForeignKey(User,related_name='sent_messages',on_delete=models.CASCADE,null=False)
    receiver = models.ForeignKey(User,related_name='received_messages',on_delete=models.CASCADE,null=False)
    sent_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=1000,null=False)
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f"sent by {self.sender.name}, content [{self.content}]"
    