from django.db import models
from accounts.models import User, userProfile
from accounts.utils import send_notification
from datetime import time

# Create your models here.
class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(userProfile, related_name='userprofile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)
   
    def __str__(self):
        return self.vendor_name

    def save(self, *args, **kwargs):
        if self.pk is not None:
            orig = Vendor.objects.get(pk=self.pk)
            if orig.is_approved != self.is_approved:
                if self.is_approved == True:
                    #send notification mail to vendor
                    mail_subject = 'Your restaurant has been approved'
                    mail_template = 'accounts/emails/admin_approval_email.html'
                    context = {
                        'user': self.user,
                        'is_approved': self.is_approved,
                        'to_email':self.user.email,
                    }
                    send_notification(mail_subject, mail_template, context)
                else:
                    #send rejection mail to vendor
                    mail_subject = 'Sorry! you are not eligible.'
                    mail_template = 'accounts/emails/admin_approval_email.html'
                    context = {
                        'user': self.user,
                        'is_approved': self.is_approved,
                    }
                    
                    send_notification(mail_subject, mail_template, context)
               
        return super(Vendor, self).save(*args, **kwargs)

DAYS = [
    (1,("Monday")),
    (2,("Tuesday")),
    (3,("Wednesday")),
    (4,("Thursday")),
    (5,("Friday")),
    (6,("Satday")),
    (7,("Sunday")),
]

HOUR_OFDAY_24 = [(time(h,m).strftime('%I:%M %p'),time(h,m).strftime('%I:%M %p')) for h in range(0,24) for m in (0,30)]

class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOUR_OFDAY_24, max_length=10, blank=True)
    to_hour = models.CharField(choices=HOUR_OFDAY_24, max_length=10, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day', '-from_hour')
        unique_together = ('vendor','day', 'from_hour','to_hour')

    def __str__(self):
        return self.get_day_display()





