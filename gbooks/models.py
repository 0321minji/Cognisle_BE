from django.db import models


class GuestBook(models.Model):
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='guestbooks')
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner.username}'s Guestbook - {self.title}"

    def message_count(self):
        return self.messages.count()

class Message(models.Model):
    guestbook = models.ForeignKey(GuestBook, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey('users.User', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.author.username} on {self.guestbook.title}"