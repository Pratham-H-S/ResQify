from django.views.generic import ListView
from django.views import View
from django.shortcuts import render, redirect
from .models import *
import googlemaps
from django.conf import settings
from .forms import *
from datetime import datetime
from Crypto.Cipher import AES
from argon2 import PasswordHasher
from Crypto.Random import get_random_bytes 

class HomeView(ListView):
    template_name = "project_content/home.html"
    context_object_name = 'mydata'
    model = Locations
    success_url = "/"

class MapView(View): 
    template_name = "project_content/map.html"

    def get(self,request): 
        key = settings.GOOGLE_API_KEY
        eligable_locations = Locations.objects.filter(place_id__isnull=False)
        locations = []

        for a in range(0,1): 
            data = {
                'lat':float(12.9175461), 
                'lng': float(77.4976599), 
                'name': 'maylasandra',
            }

            locations.append(data)


        context = {
            "key":key, 
            "locations": locations
        }

        return render(request, self.template_name, context)

class DistanceView(View):
    template_name = "project_content/distance.html"

    def get(self, request): 
        form = DistanceForm
        distances = Distances.objects.all()
        context = {
            'form':form,
            'distances':distances
        }

        return render(request, self.template_name, context)

    def post(self, request): 
        form = DistanceForm(request.POST)
        if form.is_valid(): 
            from_location = form.cleaned_data['from_location']
            from_location_info = Locations.objects.get(name=from_location)
            from_adress_string = str(from_location_info.adress)+", "+str(from_location_info.zipcode)+", "+str(from_location_info.city)+", "+str(from_location_info.country)

            to_location = form.cleaned_data['to_location']
            to_location_info = Locations.objects.get(name=to_location)
            to_adress_string = str(to_location_info.adress)+", "+str(to_location_info.zipcode)+", "+str(to_location_info.city)+", "+str(to_location_info.country)

            mode = form.cleaned_data['mode']
            now = datetime.now()

            gmaps = googlemaps.Client(key= settings.GOOGLE_API_KEY)
            calculate = gmaps.distance_matrix(
                    from_adress_string,
                    to_adress_string,
                    mode = mode,
                    departure_time = now
            )


            duration_seconds = calculate['rows'][0]['elements'][0]['duration']['value']
            duration_minutes = duration_seconds/60

            distance_meters = calculate['rows'][0]['elements'][0]['distance']['value']
            distance_kilometers = distance_meters/1000

            if 'duration_in_traffic' in calculate['rows'][0]['elements'][0]: 
                duration_in_traffic_seconds = calculate['rows'][0]['elements'][0]['duration_in_traffic']['value']
                duration_in_traffic_minutes = duration_in_traffic_seconds/60
            else: 
                duration_in_traffic_minutes = None

            
            obj = Distances(
                from_location = Locations.objects.get(name=from_location),
                to_location = Locations.objects.get(name=to_location),
                mode = mode,
                distance_km = distance_kilometers,
                duration_mins = duration_minutes,
                duration_traffic_mins = duration_in_traffic_minutes
            )

            obj.save()

        else: 
            print(form.errors)
        
        return redirect('my_distance_view')


class GeocodingView(View):
    template_name = "project_content/geocoding.html"

    def get(self,request,pk): 
        location = Locations.objects.get(pk=pk)

        if location.lng and location.lat and location.place_id != None: 
            lat = location.lat
            lng = location.lng
            place_id = location.place_id
            label = "from my database"

        elif location.adress and location.country and location.zipcode and location.city != None: 
            adress_string = str(location.adress)+", "+str(location.zipcode)+", "+str(location.city)+", "+str(location.country)

            gmaps = googlemaps.Client(key = settings.GOOGLE_API_KEY)
            result = gmaps.geocode(adress_string)[0]
            
            lat = result.get('geometry', {}).get('location', {}).get('lat', None)
            lng = result.get('geometry', {}).get('location', {}).get('lng', None)
            place_id = result.get('place_id', {})
            label = "from my api call"

            location.lat = lat
            location.lng = lng
            location.place_id = place_id
            location.save()

        else: 
            result = ""
            lat = ""
            lng = ""
            place_id = ""
            label = "no call made"

        context = {
            'location':location,
            'lat':lat, 
            'lng':lng, 
            'place_id':place_id, 
            'label': label
        }
        
        return render(request, self.template_name, context)

# views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # This is used to exempt the view from CSRF protection. Use it cautiously.
def save_location(request):
    variable = request.COOKIES.get("myVariable")
    print(variable)
    if request.method == 'POST':
        try:
            data = request.POST  # Use request.POST to access form data
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            print(latitude)
            print(longitude)
            # You can now do something with the latitude and longitude, such as saving it to the database
            # Example: Save to a model
            # location = UserLocation(latitude=latitude, longitude=longitude)
            # location.save()

            return JsonResponse({'status': 'Location saved successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return render(request,"project_content/new.html")


def login_final(request):
    if request.method == 'POST':
        data = request.POST
        name = request.POST["name"]
        print(name)
        return render(request,"project_content/login_final.html")
    return render(request,"project_content/login_final.html")


# def register(response):
#     if response.method == "POST":
#         form = RegisterForm(response.POST)
#         if form.is_valid():
#             form.save()
#             return redirect("/home")
#         else:
#             form = RegisterForm()
#     return render(response, "project_content/test_register.html", {"form":form})

    
from django.contrib.auth import authenticate, login


def signup(request):
    if request.method == 'POST':
        username = request.POST['name']
        email = request.POST['email']
        password = request.POST['pass1']
        mobile = request.POST['phone']

        hasher = PasswordHasher()
        hashed_password = hasher.hash(password)
        new_customer = UsersCustomer(username=username, email=email, password=hashed_password,mobile = mobile)
        new_customer.save()
        # UsersCustomer.save(Username = username,Email = email,Password =password)
        print(username)
        return render(request,"project_content/login_final.html")
    
      # Redirect to your home page

    # if request.method == 'POST':
    #     username = request.POST['username']
    #     password = request.POST['password']
    #     confirm_password = request.POST['confirm_password']

    #     # Check if the username already exists
    #     if User.objects.filter(username=username).exists():
            
    #         return redirect('signup')

    #     # Check if passwords match
    #     if password != confirm_password:
    #         messages.error(request, 'Passwords do not match.')
    #         return redirect('signup')

    #     # Create the user
    #     user = User.objects.create_user(username=username, password=password)

    #     # You can add additional logic here (e.g., sending a welcome email)
        
    #     messages.success(request, 'Account created successfully. You can now log in.')
    #     return redirect('login') 

    return render(request, 'project_content/login_final.html')

# from django.shortcuts import render, redirect
# from .models import Customer

# def signup(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
        
#         # Add additional customer fields here...
        
#         # # Validate user input
#         # if not username or not email or not password:
#         #     error = "Please fill out all required fields."
#         #     return render(request, 'project_content/signup.html', {'error': error})
        
#         # # Check for existing username or email
#         # try:
#         #     existing_user = UsersCustomer.objects.get(username=username)
#         #     error = "Username already exists."
#         #     return render(request, 'project_content/signup.html', {'error': error})
#         # except UsersCustomer.DoesNotExist:
#         #     pass
#         # try:
#         #     existing_user = UsersCustomer.objects.get(email=email)
#         #     error = "Email already exists."
#         #     return render(request, 'project_content/signup.html', {'error': error})
#         # except UsersCustomer.DoesNotExist:
#         #     pass
        
#         # Create new customer
#         new_customer = UsersCustomer(username=username, email=email, password=password)
#         new_customer.save()
        
#         return render(request, 'project_content/signup.html')
#     else:
#         return render(request, 'project_content/signup.html')
    # return render(request, 'project_content/signup.html')


def home(request):
    return render(request,'project_content/navbar.html')

