from django.http import HttpResponse
from backend import start
from threading import Thread


def index(request):
    Thread(target=start).start()
    return HttpResponse("<h1>Application is starting...</h1>")
