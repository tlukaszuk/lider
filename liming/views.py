from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import Http404
from django.http import JsonResponse

import datetime

# generowanie pdfow
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from .forms import ApplicationRateForm, FarmerForm, GrowingFieldForm, OrderForm
from .models import ApplicationRate, GrowingField, Farmer


# def home(request):
#     next = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
#     return render(request, 'home.html', {'next':next})


def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')
    if request.method == "POST":
        next = request.POST.get('next', settings.LOGIN_REDIRECT_URL)
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(next)
        context = {'next':next, 'login_form':form, 'login_error': True}
    else:
        next = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
        form = AuthenticationForm()
        context = {'next':next, 'login_form':form}
    return render(request, 'home.html', context)


def account_login(request):
    user = authenticate(
        username='operator1',
        password='passwd321',
    )
    login(request, user)
    next = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
    return redirect(next)


def account_logout(request):
    logout(request)
    return redirect('home')


@login_required
def form(request, ar_id=None):
    if request.method == 'POST':
        form = ApplicationRateForm(request.POST)
        if form.is_valid():
            application_rate = form.save(commit=False)
            application_rate.calculate_rates()
            if 'save' in request.POST:
                application_rate.operator_id = request.user.id
                try:
                    instance = ApplicationRate.objects.get(growing_field_id=application_rate.growing_field_id, operator_id=application_rate.operator_id)
                    application_rate.id = instance.id
                except ApplicationRate.DoesNotExist:
                    pass
                application_rate.save()
            form = ApplicationRateForm(instance=application_rate)
    else:
        if ar_id is not None:
            instance = get_object_or_404(ApplicationRate, pk=ar_id)
            #if instance.operator != request.user:
            #    raise Http404("Brak uprawnien")
            form = ApplicationRateForm(instance=instance)
        else:
            form = ApplicationRateForm()
    return render(request, 'form.html', {"form":form, "farmer_form":FarmerForm(), "field_form":GrowingFieldForm()})


@login_required
def remove(request, ar_id):
    instance = get_object_or_404(ApplicationRate, pk=ar_id)
    if instance.operator != request.user:
        raise Http404("Brak uprawnien")
    instance.delete()
    return redirect('history')


@login_required
def history(request):
    # application_rates = ApplicationRate.objects.filter(operator=request.user).order_by('field')
    application_rates = ApplicationRate.objects.all().order_by('farmer', 'growing_field')
    return render(request, 'history.html', {'application_rates':application_rates})


@login_required
def orders(request):
    application_rates = ApplicationRate.objects.all().order_by('farmer', 'growing_field')
    return render(request, 'orders.html', {'application_rates':application_rates})


def growing_fields_by_farmer(request):
    farmer_id = request.GET.get('farmer_id', None)
    if (farmer_id is not None) and (farmer_id != ''):
        growing_fields_dict = {gf.id:str(gf) for gf in GrowingField.objects.filter(farmer_id=farmer_id)}
    else:
        growing_fields_dict = {}
    return JsonResponse(growing_fields_dict)


def add_farmer(request):
    farmer_form = FarmerForm(request.GET)
    if farmer_form.is_valid():
        new_farmer = farmer_form.save()
        return JsonResponse({'status': 'ok', 'added': {'id': new_farmer.id, 'desc': str(new_farmer)}})
    else:
        return JsonResponse({'status': 'error'})


def add_growing_field(request):
    growing_field_form = GrowingFieldForm(request.GET)
    if growing_field_form.is_valid():
        new_growing_field = growing_field_form.save()
        return JsonResponse({'status': 'ok', 'added': {'id': new_growing_field.id, 'desc': str(new_growing_field)}})
    else:
        return JsonResponse({'status': 'error', 'desc': growing_field_form.errors})


@login_required
def create_report_pdf(request, ar_id=None):
    if request.method == 'POST':
        form = ApplicationRateForm(request.POST)
        if form.is_valid():
            application_rate = form.save(commit=False)
        else:
            return render(request, 'form.html', {"form":form, "farmer_form":FarmerForm(), "field_form":GrowingFieldForm()})
    else:
        application_rate = ApplicationRate.objects.get(pk=ar_id)
    application_rate.calculate_rates()
    application_rate.operator_id = request.user.id

    template = get_template("pdfs/report.html")
    html = template.render({
        "static_dir": settings.STATIC_ROOT,
        "ar": application_rate
    })
    result = BytesIO()
    pdf = pisa.pisaDocument(
        src=BytesIO(html.encode('UTF-8')),
        dest=result,
        encoding='UTF-8'
    )
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


@login_required
def prepare_order(request, ar_ids=None):
    if request.method == 'POST':
        form = ApplicationRateForm(request.POST)
        if form.is_valid():
            application_rate = form.save(commit=False)
            application_rates = [application_rate,]
        else:
            return render(request, 'form.html', {"form":form, "farmer_form":FarmerForm(), "field_form":GrowingFieldForm()})
    else:
        application_rates = [ApplicationRate.objects.get(pk=int(ar_id)) for ar_id in ar_ids.split(',')]

    farmer = application_rates[0].farmer
    growing_fields = []
    lider_ca_weight = 0
    lider_mg_weight = 0
    one_farmer = True
    for ar in application_rates:
        if ar.farmer != farmer:
            one_farmer = False
        growing_fields.append(ar.growing_field)
        ar.calculate_rates()
        if ar.pha_lider_ca_application_rate_per_field is not None:
            lider_ca_weight += ar.pha_lider_ca_application_rate_per_field
        if ar.cn_lider_mg_application_rate_per_field is not None:
            lider_mg_weight += ar.cn_lider_mg_application_rate_per_field

    if one_farmer:
        order_form = OrderForm(initial={
            "farmer": farmer,
            "client": f"{farmer.name}\n{farmer.location}",
            "growing_fields": "\n".join([str(gf) for gf in growing_fields]),
            "lider_ca_weight": lider_ca_weight,
            "lider_mg_weight": lider_mg_weight,
            "lider_ca_price": 500.00,
            "lider_mg_price": 500.00
        })
    else:
        order_form = None

    return render(request, 'order_prepare.html', {'order_form': order_form})


@login_required
def create_order_pdf(request, save=False):
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.operator = f"{request.user.first_name} {request.user.last_name}"
            order.date = datetime.date.today()

            if save:
                order.save()

            template = get_template("pdfs/order.html")
            html = template.render({
                "static_dir": settings.STATIC_ROOT,
                "order": order
            })
            result = BytesIO()
            pdf = pisa.pisaDocument(
                src=BytesIO(html.encode('UTF-8')),
                dest=result,
                encoding='UTF-8'
            )
            if not pdf.err:
                return HttpResponse(result.getvalue(), content_type='application/pdf')
        else:
            return render(request, 'order_prepare.html', {'order_form': order_form})
    return None
