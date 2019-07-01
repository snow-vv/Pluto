import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views import View

from common.exception import PasswordMismatchException
from common.views import JsonView
from common.utils.gravatar import gravatar_url


# Create your views here.


def index(request):
    return render(request, 'index.html', {'title': '首页'})


class LoginView(View):
    def get(self, request):
        return render(request, 'accounts/login.html')

    def post(self, request):
        next_url = request.GET.get('next', '/')
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect(next_url)

        else:
            return render(request, 'accounts/login.html')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('accounts:login')


class LoginApiView(JsonView):
    login_require = False

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user = authenticate(**data)
        if user:
            login(request, user)
            return {
                "id": user.id,
                "name": user.username,
                "avatar_url": gravatar_url(
                    user.email.encode('utf-8')) or "https://adminlte.io/themes/AdminLTE/dist/img/user2-160x160.jpg",
                "created_at": "17 Aug 16:22",
                "is_superuser": user.is_superuser,
            }
        else:
            raise PasswordMismatchException


class LogoutApiView(JsonView):
    def get(self, request):
        logout(request)
        return {}


class ChangePasswordApiView(JsonView):
    def post(self, request):
        user = request.user
        data = json.loads(request.body.decode("utf-8"))
        if user.check_password(data.get('password')):
            user.set_password(data.get('new_password'))
            user.save()
            return {}
        else:
            raise PasswordMismatchException
