import datetime

from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.db.models import Max, Q

from Jobbing.models import Offer, StandardUser, Category, CompanyUser


class SearchForm(forms.Form):
    job = forms.CharField(max_length=100, required=False)
    location = forms.CharField(max_length=100, required=False)
    category = forms.CharField(max_length=100, required=False)
    job_type = forms.CharField(max_length=100, required=False)
    contract_type = forms.CharField(max_length=100, required=False)
    posted_within = forms.IntegerField(required=False)
    salary_from = forms.IntegerField(required=False)
    salary_upto = forms.IntegerField(required=False)


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    pwd = forms.CharField(required=True)


class RegisterForm(forms.Form):
    username = forms.CharField(required=True)
    pwd1 = forms.CharField(required=True)
    pwd2 = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    mail = forms.CharField(required=True)


class OfferForm(ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.filter(Q(relates_to__isnull=False)), required=True)
    edit_mode = forms.BooleanField(help_text="If selected, offer will not be public. You will be able to edit it and public later", required=False)
    class Meta:
        model = Offer
        fields = ['category', 'salary_from', 'salary_upto', 'header', 'city', 'contract_type', 'working_time', 'content', 'edit_mode']


class UploadCvForm(forms.Form):
    cv = forms.FileField(required=True)


def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')


class AccountSettingsForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.CharField(required=True)


class CompanySettingsForm(forms.Form):
    email = forms.CharField(required=True)
    company_name = forms.CharField(required=True)
    web = forms.CharField(required=True)
    about_us = forms.CharField(required=True)
    img = forms.ImageField(required=False)


class ChangePasswordForm(forms.Form):
    cpassword = forms.CharField()
    new_1 = forms.CharField()
    new_2 = forms.CharField()