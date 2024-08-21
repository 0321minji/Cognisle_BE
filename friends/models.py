from django.db import models
from users.models import User

# Create your models here.
class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_friend_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def accept(self):
        from_friend, created = Friend.objects.get_or_create(user=self.from_user)
        to_friend, created = Friend.objects.get_or_create(user=self.to_user)
        
        from_friend.friends.add(self.to_user)
        to_friend.friends.add(self.from_user)
        
        self.delete()

    def reject(self):
        self.delete()
        
class Friend(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    friends = models.ManyToManyField(User, symmetrical=False, related_name="friend_set", blank=True)
    def __str__(self):
        return self.user.email