from django.db import models
from Auth.models import User



class Chat(models.Model):
    user1 = models.ForeignKey(User, related_name='chats_as_user1', on_delete=models.DO_NOTHING)
    user2 = models.ForeignKey(User, related_name='chats_as_user2', on_delete=models.DO_NOTHING)
    room_name = models.CharField(max_length=100, unique=True)



    def save(self, *args, **kwargs):
       
        self.room_name = f"room_{min(self.user1.id, self.user2.id)}_{max(self.user1.id, self.user2.id)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.room_name

    @classmethod
    def get_or_create_chat(cls, user1, user2):
       
        user1, user2 = sorted([user1, user2], key=lambda x: x.id)
        
        
        chat, created = cls.objects.get_or_create(user1=user1, user2=user2)
        return chat

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user1', 'user2'],
                name='unique_chat_users_pair'
            )
        ]

class Message(models.Model):
    sender = models.ForeignKey(User,related_name='sent_messages',on_delete=models.CASCADE,null=False)
    receiver = models.ForeignKey(User,related_name='received_messages',on_delete=models.CASCADE,null=False)
    sent_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=1000,null=False)
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE, null=False)
    last_chat = models.OneToOneField('Chat', related_name='last_message', on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return f"sent by {self.sender.name}, content [{self.content}]"
    