import json
from django.http import HttpResponse
from . import login, reg
from . import ais_reg, ais_login

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

def ais_refresh(request):
    if request.method == "GET":
        country_code = request.GET.get('code', default='')
        schecule_id = request.GET.get('id', default='')
        session = request.GET.get('session', default='')
    elif requests.method == "POST":
        country_code = request.POST.get('code', default='')
        schecule_id = request.POST.get('id', default='')
        session = request.POST.get('session', default='')
    else:
        return HttpResponse('{"code": 400, "msg": "Malform Request"}')
    if len(country_code) == 0 or len(schecule_id) == 0 or len(session) == 0:
        return HttpResponse('{"code": 401, "msg": "Invalid Parameters"}')

    result, new_session = ais_login.refresh(country_code, schecule_id, session)
    if result == []:
        return HttpResponse('{"code": 402, "msg": "Session Expired"}')
    obj = {
        "code": 0,
        "msg": result,
        "session": new_session
    }
    return HttpResponse(json.dumps(obj, ensure_ascii=False))

def ais_register(request):
    if request.method == "GET":
        country_code = request.GET.get('code', default='')
        email = request.GET.get('email', default='')
        pswd = request.GET.get('pswd', default='')
        node = request.GET.get('node', default='')
    elif requests.method == "POST":
        country_code = request.POST.get('code', default='')
        email = request.POST.get('email', default='')
        pswd = request.POST.get('pswd', default='')
        node = request.POST.get('node', default='')
    else:
        return HttpResponse('{"code": 400, "msg": "Malform Request"}')
    if len(country_code) == 0 or len(email) == 0 or len(pswd) == 0:
        return HttpResponse('{"code": 401, "msg": "Missing parameters"}')

    result = session = schedule_id = None
    try:
        result, session, schedule_id = ais_reg.register(country_code, email, pswd, node)
    except Exception as e:
        print(e)
    if not result or not session or not schedule_id:
        return HttpResponse('{"code": 402, "msg": "Network Error"}')
    obj = {
        "code": 0,
        "msg": result,
        "session": session,
        "id": schedule_id
    }
    return HttpResponse(json.dumps(obj, ensure_ascii=False))
