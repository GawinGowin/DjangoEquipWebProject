from datetime import datetime
from django.shortcuts import redirect, render
from django.http import HttpRequest

year = datetime.now().year

def home(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'baseapp/index.html',
        {
            'title':'ホーム',
            'year': year,
        }
    )

def about(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'baseapp/about.html',
        {
            'title':'About',
            'message':'開発中',
            'year':year
        }
    )

def contact(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'baseapp/contact.html',
        {
            'title':'Contact',
            'message':'Related Sites',
            'year': year,
        }
    )

from django.contrib.auth.views import LoginView
from baseapp import forms

class login(LoginView):
    template_name='baseapp/login.html'
    authentication_form=forms.BootstrapAuthenticationForm
    extra_context={'title': 'Log in',
                   'year' : year,
                   }

from django.contrib.auth.models import User
from django.db import IntegrityError

#GETとPOSTの違い
#https://blog.senseshare.jp/get-post-method.html


def signup(request):
    assert isinstance(request, HttpRequest)
    form = forms.BootstrapAuthenticationSignupForm()

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        mail = request.POST['mail']
        try:
            User.objects.create_user(username, mail, password)

        except IntegrityError:
            return render(
                request,
                'baseapp/signup.html',
                {
                    'error': 'このユーザーは登録されています',
                    'title': 'Sign up',
                    'year' : year,
                    'form': form,
                },
            )
    else:
        return render(
            request,
            'baseapp/signup.html',
            {
                'title': 'Sign up',
                'year' : year,
                'form': form,
            }
        )

    return redirect(home)
