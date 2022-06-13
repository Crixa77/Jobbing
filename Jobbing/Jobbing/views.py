import magic
import mimetypes
import os
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMessage
from django.db.models import Max, Q
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader

from .forms import SearchForm, LoginForm, OfferForm, UploadCvForm, AccountSettingsForm, ChangePasswordForm, \
    RegisterForm, CompanySettingsForm
from .models import Category, Offer, WorkingTime, ContractType, AppConf, StandardUser, AppSettings, JobApplication


# Create your views here.

def currentOffers():
    return Offer.objects.filter(ended_at__gt=datetime.now()).filter(edit_mode=False).order_by('-updated_at')

def userDisabledOffers(user):
    return Offer.objects.filter(company__user__id=user.id).filter(Q(ended_at__lt=datetime.now()) | Q(edit_mode=True))


def getAppSettings():
    dbdata = AppConf.objects.all()
    appSettings = AppSettings(
        dbdata.filter(conf_key='contact_time_to_contact')[0].value,
        dbdata.filter(conf_key='contact_phone')[0].value,
        dbdata.filter(conf_key='contact_email')[0].value,
        dbdata.filter(conf_key='contact_addr_2')[0].value,
        dbdata.filter(conf_key='contact_addr_1')[0].value,
        dbdata.filter(conf_key='about_us')[0].value,
        dbdata.filter(conf_key='footer_about_us')[0].value,
        dbdata.filter(conf_key='app_title')[0].value,
        dbdata.filter(conf_key='footer_newsletter')[0].value)
    return appSettings


def loginUser(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['pwd']
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)
                return redirect('index')
        messages.add_message(request, messages.WARNING, "Failed to login")
    return redirect('index')


def logoutUser(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect(index)


def index(request):
    category_list = Category.objects.all().filter(relates_to=None)[:5]
    offer_list = currentOffers()[:5]
    city_list = Offer.objects.values('city').distinct()
    template = loader.get_template('Jobbing/index.html')
    context = {
        'category_list': category_list,
        'offer_list': offer_list,
        'city_list': city_list,
        'user': request.user,
        'appConf': getAppSettings()
    }
    return HttpResponse(template.render(context, request))


def job_details(request, id):
    template = loader.get_template('Jobbing/job_details.html')
    try:
        job = currentOffers().filter(id=id)
        if job.count() > 0:
            context = {
                'job': job[0],
                'user': request.user,
                'appConf': getAppSettings()
            }
            return HttpResponse(template.render(context, request))
        else:
            job = Offer.objects.filter(id=id)
            if len(job) > 0:
                if request.user.companyuser.id == job[0].company.id:
                    context = {
                        'job': job[0],
                        'user': request.user,
                        'appConf': getAppSettings()
                    }
                    return HttpResponse(template.render(context, request))
            messages.add_message(request, messages.WARNING, "Offer does not exist")
            return redirect('index')
    except:
        messages.add_message(request, messages.ERROR, "Something went wrong")
        return redirect('index')


def search(request):
    jobs = None
    template = loader.get_template('Jobbing/job_listing.html')
    categories = Category.objects.all()
    working_time = WorkingTime.objects.all()
    contract_types = ContractType.objects.all()
    city_list = currentOffers().values('city').distinct().order_by()
    salary_max = currentOffers().aggregate(Max('salary_upto'))['salary_upto__max']
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            try:
                location = form.cleaned_data['location']
                job = form.cleaned_data['job']
                category = form.cleaned_data['category']
                job_type = form.cleaned_data['job_type']
                contract_type = form.cleaned_data['contract_type']
                posted_within = form.cleaned_data['posted_within']
                salary_from = form.cleaned_data['salary_from']
                salary_upto = form.cleaned_data['salary_upto']
                jobs = currentOffers()
                if len(location) > 0:
                    jobs = jobs.filter(city=location)
                if len(job) > 0:
                    jobs = jobs.filter(header__contains=job)
                if len(category) > 0:
                    jobs = jobs.filter(Q(category=category) | Q(category__relates_to=category))
                if len(contract_type) > 0:
                    jobs = jobs.filter(contract_type=contract_type)
                if len(job_type) > 0:
                    jobs = jobs.filter(working_time=job_type)
                if posted_within is not None:
                    jobs = jobs.filter(updated_at__gte=datetime.now() - timedelta(days=7))
                if salary_from is not None:
                    jobs = jobs.filter(salary_upto__gte=salary_from)
                if salary_upto is not None:
                    jobs = jobs.filter(salary_from__lte=salary_upto)
            except:
                messages.add_message(request, messages.ERROR, "Search failed")
                redirect('search')
        else:
            messages.add_message(request, messages.ERROR, "Form is not valid")
            redirect('search')

    else:
        jobs = currentOffers()
        category = request.GET.get('cat', '')
        if len(category) > 0:
            jobs = jobs.filter(Q(category=category) | Q(category__relates_to=category))

    context = {
        'jobs': jobs,
        'categories': categories,
        'working_time': working_time,
        'contract_types': contract_types,
        'salary_max': salary_max,
        'city_list': city_list,
        'user': request.user,
        'appConf': getAppSettings()

    }
    return HttpResponse(template.render(context, request))


def about(request):
    about = AppConf.objects.all()
    about = about.filter(conf_key="about_us")
    context = {
        'user': request.user,
        'about_us': about[0].value,
        'appConf': getAppSettings()
    }
    template = loader.get_template('Jobbing/about.html')
    return HttpResponse(template.render(context, request))


def contact(request):
    contact_details = AppConf.objects.all()
    contact_time_to_contact = contact_details.filter(conf_key="contact_time_to_contact")
    contact_phone = contact_details.filter(conf_key="contact_phone")
    contact_email = contact_details.filter(conf_key="contact_email")
    contact_addr_2 = contact_details.filter(conf_key="contact_addr_2")
    contact_addr_1 = contact_details.filter(conf_key="contact_addr_1")
    context = {
        'user': request.user,
        'contact_time_to_contact': contact_time_to_contact[0].value,
        'contact_phone': contact_phone[0].value,
        'contact_email': contact_email[0].value,
        'contact_addr_2': contact_addr_2[0].value,
        'contact_addr_1': contact_addr_1[0].value,
        'appConf': getAppSettings()
    }
    template = loader.get_template('Jobbing/contact.html')
    return HttpResponse(template.render(context, request))


def add_offer(request):
    if request.user.is_authenticated and request.user.companyuser is not None:
        if request.method == 'GET':
            form = OfferForm()
            categories = Category.objects.all()
            template = loader.get_template('Jobbing/add_offer.html')
            context = {
                "user": request.user,
                "form": form,
                "categories": categories,
                'appConf': getAppSettings()
            }
            return HttpResponse(template.render(context, request))
        if request.method == 'POST':
            form = OfferForm(request.POST)
            if form.is_valid():
                try:
                    offer = form.save(commit=False)
                    offer.company_id = request.user.companyuser.id
                    offer.ended_at = datetime.now() + timedelta(days=14)
                    offer.save()
                    messages.add_message(request, messages.INFO, "Offer added")
                except Exception as exc:
                    print(exc)
                    messages.add_message(request, messages.ERROR, "Failed to add offer")
            else:
                messages.add_message(request, messages.ERROR, "Form is not valid")
            return redirect('index')
    else:
        messages.add_message(request, messages.ERROR, 'You are not authorized, request business account.')
        return redirect('index')


def edit_offer(request, offerid):
    if request.user.is_authenticated and request.user.companyuser is not None:
        if request.method == 'GET':
            offer = Offer.objects.filter(id=offerid)
            if offer[0].company.id == request.user.companyuser.id:
                offer = offer[0]
                form = OfferForm(model_to_dict(offer))
                categories = Category.objects.all()
                template = loader.get_template('Jobbing/add_offer.html')
                context = {
                    "user": request.user,
                    "form": form,
                    "categories": categories,
                    'appConf': getAppSettings()
                }
                return HttpResponse(template.render(context, request))
            else:
                messages.add_message(request, messages.ERROR, 'You are not authorized to edit this offer.')
                return redirect('index')
        if request.method == 'POST':
            offer_to_edit = Offer.objects.filter(id=offerid)
            form = OfferForm(request.POST or None, instance=offer_to_edit[0])
            if form.is_valid():
                try:
                    if offer_to_edit[0].company.id == request.user.companyuser.id:
                        offer = form.save(commit=False)
                        offer.ended_at = datetime.now() + timedelta(days=14)
                        offer.save()
                        messages.add_message(request, messages.INFO, "Offer edited")
                    else:
                        messages.add_message(request, messages.ERROR, 'You are not authorized to edit this offer.')
                        return redirect('index')
                except Exception as exc:
                    print(exc)
                    messages.add_message(request, messages.ERROR, "Failed to add offer")
            else:
                messages.add_message(request, messages.ERROR, "Form is not valid")
            return redirect('your_offers')
    else:
        messages.add_message(request, messages.ERROR, 'You are not authorized, request business account.')
        return redirect('index')


def account_settings(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            context = {
                'user': request.user,
                'appConf': getAppSettings()
            }
            template = loader.get_template('Jobbing/account_settings.html')
            return HttpResponse(template.render(context, request))
        if request.method == 'POST':
            form = AccountSettingsForm(request.POST)
            if form.is_valid():
                try:
                    request.user.first_name = form.cleaned_data['first_name']
                    request.user.last_name = form.cleaned_data['last_name']
                    request.user.email = form.cleaned_data['email']
                    request.user.save()
                    messages.add_message(request, messages.INFO, "Account details saved")
                except:
                    messages.add_message(request, messages.ERROR, "Failed to change account details")
            return redirect('account_settings')
        return redirect('index')
    else:
        messages.add_message(request, messages.ERROR, "Please login before change settings")
        return redirect('index')


def company_settings(request):
    if request.user.is_authenticated and request.user.companyuser is not None:
        if request.method == 'POST':
            form = CompanySettingsForm(request.POST or None, request.FILES or None)
            if form.is_valid():
                try:
                    request.user.companyuser.company_name = form.cleaned_data['company_name']
                    request.user.companyuser.web = form.cleaned_data['web']
                    request.user.companyuser.about_us = form.cleaned_data['about_us']
                    if 'img' in form.files:
                        if request.user.companyuser.img:
                            os.remove(os.path.join(settings.MEDIA_ROOT, request.user.companyuser.img.name))
                        request.user.companyuser.img = form.files['img']
                    request.user.companyuser.save()
                    request.user.email = form.cleaned_data['email']
                    request.user.save()
                    messages.add_message(request, messages.INFO, "Account details saved")
                except Exception as ex:
                    print(ex)
                    messages.add_message(request, messages.ERROR, "Failed to change account details")
            else:
                messages.add_message(request, messages.ERROR, "Form is not valid")
                messages.add_message(request, messages.ERROR, form.errors)
            return redirect('account_settings')
        return redirect('index')
    else:
        messages.add_message(request, messages.ERROR, "Please login before change settings")
        return redirect('index')


def upload_cv(request):
    if request.user.is_authenticated and request.user.standarduser is not None:
        if request.method == 'POST':
            form = UploadCvForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    request.user.standarduser.cv = form.files['cv']
                    request.user.standarduser.save()
                    messages.add_message(request, messages.INFO, "CV added")
                    return redirect("index")
                except:
                    messages.add_message(request, messages.ERROR, "Failed to add CV")
                    return redirect("index")
            else:
                messages.add_message(request, messages.ERROR, "Invalid file")
                return redirect("index")
    messages.add_message(request, messages.ERROR, "Not available")
    return redirect("index")


def change_password(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ChangePasswordForm(request.POST)
            if form.is_valid():
                pwd = form.cleaned_data['cpassword']
                new_1 = form.cleaned_data['new_1']
                new_2 = form.cleaned_data['new_2']
                if request.user.check_password(pwd) and new_1 == new_2:
                    try:
                        user = request.user
                        user.set_password(form.cleaned_data['new_1'])
                        user.save()
                        messages.add_message(request, messages.INFO, "Password changed")
                        return redirect('index')
                    except:
                        messages.add_message(request, messages.ERROR, "Failed to change password")
                else:
                    messages.add_message(request, messages.ERROR,
                                         "Wrong current password, or new password are not the same")
            else:
                messages.add_message(request, messages.ERROR, "Form is not valid")
            return redirect('account_settings')
        return redirect('index')
    else:
        messages.add_message(request, messages.ERROR, "Please login before try to change password")
        return redirect('index')


def get_cv(request):
    if request.user.is_authenticated and request.user.standarduser is not None:
        try:
            filename = request.user.standarduser.cv.name.split('/')[-1]
            response = HttpResponse(request.user.standarduser.cv, content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
            return response
        except:
            messages.add_message(request, messages.ERROR, "Failed to download CV.")
    else:
        messages.add_message(request, messages.ERROR, "Login before downloading your CV.")
        return redirect('index')


def register(request):
    if request.method == 'POST' and request.user.is_authenticated == False:
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            mail = form.cleaned_data['mail']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            pwd1 = form.cleaned_data['pwd1']
            pwd2 = form.cleaned_data['pwd2']
            if pwd1 == pwd2:
                user = User(username=username, email=mail, first_name=first_name, last_name=last_name)
                user.set_password(pwd1)
                user.save()
                user = authenticate(username=username, password=pwd1)
                if user is not None and user.is_active:
                    login(request, user)
                    user = request.user
                    standarduser = StandardUser(user=user)
                    standarduser.save()
                    messages.add_message(request, messages.INFO, "Account created")
                    return redirect('index')
                else:
                    messages.add_message(request, messages.ERROR, "Something went wrong")
                    return redirect('index')
            else:
                messages.add_message(request, messages.ERROR, "Passwords does not match")
                return redirect('index')
        else:
            messages.add_message(request, messages.ERROR, form.errors)
            return redirect('index')
    else:
        return redirect('index')


def apply(request, offerid):
    if request.user.is_authenticated and request.user.standarduser is not None and request.method == 'GET':
        try:
            ja = JobApplication(offer_id=offerid, user_id=request.user.id)
            offer = Offer.objects.filter(id=offerid)[0]
            ja.save()
            mail = EmailMessage('New application: ' + offer.header,
                                request.user.first_name + ' ' + request.user.last_name + ' applied. CV in attachment',
                                settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
            filename = os.path.join(settings.MEDIA_ROOT, request.user.standarduser.cv.file.name)
            content = open(request.user.standarduser.cv.file.name, 'rb').read()
            mime = magic.Magic(mime=True)
            mail.attach(filename, content, mime.from_file(filename))
            mail.send()
            messages.add_message(request, messages.INFO, "Sent CV")
            return redirect('index')
        except Exception as inst:
            messages.add_message(request, messages.ERROR, "Failed to apply")
            return redirect("index")
    else:
        return redirect('index')


def your_offers(request):
    if request.user.companyuser:
        offer_list = currentOffers().filter(company__user__id=request.user.id)
        disabled_offers = userDisabledOffers(request.user)
        template = loader.get_template('Jobbing/your_offers.html')
        context = {
            'offer_list': offer_list,
            'disabled_offers': disabled_offers,
            'user': request.user,
            'appConf': getAppSettings()
        }
        return HttpResponse(template.render(context, request))
    else:
        return('index')


def request_company(request):
    if request.user.is_authenticated and hasattr(request.user, 'companyuser') is False and request.method == 'GET':
        try:
            send_mail('Request for company account',
            request.user.first_name + ' ' + request.user.last_name + ' applied for company account. Email: ' + request.user.email,
            settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
            messages.add_message(request, messages.INFO, "Request sent. Administrator with contact you on your email.")
            return redirect('index')
        except Exception as inst:
            print(inst)
            messages.add_message(request, messages.ERROR, "Failed to request.")
            return redirect("index")
    else:
        return redirect('index')


def delete_offer(request, offerid):
    offer = Offer.objects.filter(id=offerid)
    if offer[0].company.id == request.user.companyuser.id:
        offer[0].delete()
        return redirect('your_offers')
    else:
        messages.add_message(request, messages.ERROR, "You have no privileges to delete that offer.")
        return redirect("index")


def activate_offer(request, offerid):
    offer = Offer.objects.filter(id=offerid)
    if offer[0].company.id == request.user.companyuser.id:
        offer = offer[0]
        offer.ended_at = datetime.now() + timedelta(14)
        offer.edit_mode = False
        offer.save()
        return redirect('your_offers')
    else:
        messages.add_message(request, messages.ERROR, "You have no privileges to activate that offer.")
        return redirect("index")


def deactivate_offer(request, offerid):
    offer = Offer.objects.filter(id=offerid)
    if offer[0].company.id == request.user.companyuser.id:
        offer = offer[0]
        offer.edit_mode = True
        offer.save()
        return redirect('your_offers')
    else:
        messages.add_message(request, messages.ERROR, "You have no privileges to deactivate that offer.")
        return redirect("index")


def flaticons(request):
    context = {'user': request.user}
    template = loader.get_template('Jobbing/flaticons.html')
    return HttpResponse(template.render(context, request))
