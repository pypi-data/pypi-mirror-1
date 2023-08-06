# Create your views here.
from django.http import HttpResponse

def auth(request):
    import pdb
    pdb.set_trace()
    return HttpResponse(status=401)
