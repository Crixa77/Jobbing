import os
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django_resized import ResizedImageField
from tinymce.models import HTMLField


# Create your models here.
def update_filename_cv(instance, filename):
    filename, file_extension = os.path.splitext(filename)
    path = "upload/cv/"
    if os.path.exists(instance.user.username + "_CV" + file_extension):
        os.remove(instance.user.username + "_CV" + file_extension)
    format = instance.user.username + "_CV" + file_extension
    return os.path.join(path, format)


def update_filename_img(instance, filename):
    filename, file_extension = os.path.splitext(filename)
    path = "upload/company_img/"
    if os.path.exists(instance.user.username + "_CV" + file_extension):
        os.remove(instance.user.username + "_CV" + file_extension)
    format = instance.user.username + "_CV" + file_extension
    return os.path.join(path, format)


class StandardUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cv = models.FileField(upload_to=update_filename_cv, null=True, blank=True)
    preferences = models.TextField(null=True, blank=True)


class CompanyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=50, unique=True)
    web = models.CharField(max_length=50, unique=True, null=True, blank=True)
    img = ResizedImageField(size=[85, 85], null=True, upload_to=update_filename_img, blank=True)
    about_us = HTMLField(null=True)

    def __str__(self):
        return self.company_name


class Category(models.Model):
    category = models.CharField(max_length=50, unique=True)
    relates_to = models.ForeignKey(to='self', on_delete=models.CASCADE, null=True, related_name='subcategory', blank=True)
    ico = models.CharField(max_length=50, default="", null=True, blank=True)
    count = models.IntegerField(default=0)

    @property
    def offer_count(self):
        count = 0
        count += Offer.objects.filter(category_id=self.id).filter(edit_mode=False).count()
        childrens = Category.objects.filter(relates_to__id=self.id)
        if len(childrens) > 0:
            for c in childrens:
                count += c.offer_count
        return count

    def __str__(self):
        if self.relates_to is not None:
            return self.category + " (" + str(self.relates_to) + ")"
        else:
            return self.category


class WorkingTime(models.Model):
    working_time = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.working_time


class ContractType(models.Model):
    job_type = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.job_type


class Offer(models.Model):
    company = models.ForeignKey(CompanyUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    salary_from = models.PositiveIntegerField()
    salary_upto = models.PositiveIntegerField()
    header = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=False, blank=False, default=datetime.now())
    city = models.CharField(max_length=50)
    contract_type = models.ForeignKey(ContractType, on_delete=models.SET_NULL, null=True)
    working_time = models.ForeignKey(WorkingTime, on_delete=models.SET_NULL, null=True)
    content = HTMLField()
    edit_mode = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return self.header


class JobApplication(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    user = models.ForeignKey(StandardUser, on_delete=models.SET_NULL, null=True)


class AppConf(models.Model):
    conf_key = models.CharField(max_length=50, unique=True, primary_key=True, editable=False)
    value = HTMLField(null=True)

    def __str__(self):
        return self.conf_key


class AppSettings():
    def __init__(self, contact_time_to_contact, contact_phone, contact_email, contact_addr_2, contact_addr_1, about_us, footer_about_us, app_title, footer_newsletter):
        self.footer_newsletter = footer_newsletter
        self.app_title = app_title
        self.footer_about_us = footer_about_us
        self.about_us = about_us
        self.contact_addr_1 = contact_addr_1
        self.contact_addr_2 = contact_addr_2
        self.contact_email = contact_email
        self.contact_phone = contact_phone
        self.contact_time_to_contact = contact_time_to_contact