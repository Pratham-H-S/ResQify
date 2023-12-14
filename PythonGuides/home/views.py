from django.shortcuts import render
from django.http import HttpResponse
from. models import *
from home.encrypt_util import *

def register(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        print('Original Password:', request.POST['password'])
        encryptpass= encrypt(request.POST['password'])
        print('Encrypt Password:',encryptpass)
        decryptpass= decrypt(encryptpass)
        print('Decrypt Password:',decryptpass)
        data=EmpLogin(name=name, email=email, password=password)
        data = UsersCustomer(name=name)
        data.save()
        return HttpResponse('Done')
    else:
        return render(request, 'login_final.html')


def signup(request):
    if  request.method == 'POST':
        name = request.POST['name']
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        password1 = request.POST['pass1']
        password2 = request.POST['pass2']
        if password1 != password2:
            encryptpass= encrypt(password1)
            data = UsersCustomer(name=name,username=username,email=email,mobile=phone,password= encryptpass)
            data.save()
            return render(request, 'login_final.html')
        else:
            return render(request, 'login_final.html')
        
    
    return render(request, 'login_final.html')

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        verify = UsersCustomer.objects.get(username = username)
        print(verify.username)
        # if (verify == username):
        #     print(username)
        return HttpResponse("done")

    return render(request,'login_final.html')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # This is used to exempt the view from CSRF protection. Use it cautiously.
def save_location(request):
    # variable = request.COOKIES.get("myVariable")
    # long = request.COOKIES.get("long")
    # print(variable)
    # print(long)
    if request.method == 'POST':
        try:
            # data = request.POST  # Use request.POST to access form data
            # latitude = data.get('lat')
            # longitude = data.get('long')
            # print(latitude)
            # print(longitude)
            # You can now do something with the latitude and longitude, such as saving it to the database
            # Example: Save to a model
            # location = UserLocation(latitude=latitude, longitude=longitude)
            # location.save()
            lat = request.COOKIES.get("myVariable")
            long = request.COOKIES.get("long")
            l = lat.split(',')
            lat= l[0]
            print(lat)
            print(long)
           

            key = settings.GOOGLE_API_KEY
            # eligable_locations = Locations.objects.filter(place_id__isnull=False)
            locations = []

            for a in range(0,1): 
                data = {
                    "lat":float(lat), 
                    "lng": float(long), 
                    "name":'',
                    
                }

                locations.append(data)


            context = {
                "key": key, 
                "locations": locations
            }

            return render(request, 'customer_map.html', context)


            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return render(request,"location.html")
    
