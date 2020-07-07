from django.http import HttpResponse
from django.shortcuts import render_to_response
from . import login, reg

def index(request):
    return HttpResponse('{"code": 0, "msg": "OK"}')

def refresh(request):
    if request.method == "GET":
        sess = request.GET.get('session', default='')
    elif requests.method == "POST":
        sess = request.POST.get('session', default='')
    else:
        return HttpResponse('{"code": 400, "msg": "Malform Request"}')
    if len(sess) == 0:
        return HttpResponse('{"code": 401, "msg": "No Session Spcified"}')

    date = login.do_login(sess)
    if not date:
        return HttpResponse('{"code": 402, "msg": "Session Expired"}')
    return HttpResponse('{"code": 0, "msg": "%d-%d-%d"}' % (date[0], date[1], date[2]))

def register(request):
    if request.method == "GET":
        visa_type = request.GET.get('type', default='')
        place = request.GET.get('place', default='')
    elif requests.method == "POST":
        visa_type = request.POST.get('type', default='')
        place = request.POST.get('place', default='')
    else:
        return HttpResponse('{"code": 400, "msg": "Malform Request"}')
    if len(visa_type) == 0 or len(place) == 0:
        return HttpResponse('{"code": 401, "msg": "Missing parameters"}')

    sess = date = None
    try:
        sess, date = reg.do_register(visa_type, place)
    except Exception as e:
        print(e)
    if not sess or not date:
        return HttpResponse('{"code": 402, "msg": "Network Error"}')
    return HttpResponse('{"code": 0, "msg": "%d-%d-%d", "session": "%s"}' % (date[0], date[1], date[2], sess))
