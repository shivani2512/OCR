from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from datetime import date, datetime


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=250, default='')
    email = models.EmailField(
        verbose_name='Email Address',
        max_length=255,
        unique=True,
    )
    Contact = models.IntegerField(null=True)
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False) # a admin user; non super-user
    admin = models.BooleanField(default=False)
    # a superuser
    # notice the absence of a "Password field", that's
    # built in.

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # Email & Password are required by default.

    class Meta:
        unique_together = (('id', 'email'),)

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin

    @property
    def is_is_active(self):
        "Is the user active?"
        return self.is_active


operations = (
    ('1', 'Simple Thresholding'),
    ('2', 'Adaptive-mean Thresholding'),
    ('3', 'Gaussian-mean Thresholding'),
    ('4', 'Otsu Thresholding'),
)


class Upload(models.Model):
    FileName = models.CharField(max_length=150, default='')
    File = models.FileField(upload_to='upload/')
    operation = models.CharField(max_length=50, choices=operations, default='1')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return self.FileName


class Output(models.Model):
    filename = models.ForeignKey(Upload, on_delete=models.CASCADE)
    # date = models.DateTimeField(auto_now_add=True)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)

    # def __str__(self):
    #     return self.filename

# class FileConfig(models.Model):
#     configName = models.CharField(max_length=50,default='')
#     user = models.ForeignKey(User,on_delete=models.CASCADE)
#     inputFolder = models.TextField(max_length=50,default='')
#     processFolder = models.TextField(max_length=50,default='')
#     outputFolder = models.TextField(max_length=50,default='')
#     operation = models.CharField(max_length=50, choices=operations, default='1')
#
#     def __str__(self):
#         return self.configName

