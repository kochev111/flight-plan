from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .forms import InputForm
from django.http import HttpResponseRedirect
from .classes import Plan
from django.http import JsonResponse
from django.core import files
from io import BytesIO
from PIL import Image

def index(request):
    # if this is a POST request we need to process the form data
    plan = Plan({})
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = InputForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            plan = Plan(form.cleaned_data)
            plan.prepare_pattern()
            img = plan.pattern
            thumb_io = BytesIO()  # create a BytesIO object
            img.save(thumb_io, 'png')
            savedImg = files.File(thumb_io, name="calculated_pattern")
            plan.pattern = savedImg
            plan.save()
            render(request, "render/get-input.html", {"form": form, "plan": plan})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = InputForm()

    return render(request, "render/index.html", {"form": form, "plan": plan})


def get_input(request):
    return render(request, "render/index.html", {"form": request.get('name'), "plan": request.get('plan')})
