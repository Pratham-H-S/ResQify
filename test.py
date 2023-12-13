from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

data = b'secret data'

key = get_random_bytes(16)
print(key)
cipher = AES.new(key, AES.MODE_EAX)
ciphertext, tag = cipher.encrypt_and_digest(data)

file_out = open("encrypted.bin", "wb")
[ file_out.write(x) for x in (cipher.nonce, tag, ciphertext) ]
file_out.close()
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, VerifyEmailSerializer, GenerateOtpSerializer
from .utils import send_otp_email

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_otp_email(user)
            return Response({"message": "Registration successful. Please verify your email."})
        return Response(serializer.errors)

class VerifyEmailView(APIView):
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            try:
                user = User.objects.get(email=email)
                if user.otp == otp and user.otp_expiry_time > timezone.now():
                    user.is_verified = True
                    user.save()
                    return Response({"message": "Email verified successfully."})
                else:
                    return Response({"message": "Invalid OTP."})
            except User.DoesNotExist:
                return Response({"message": "User not found."})
        return Response(serializer.errors)

class GenerateOtpView(APIView):
    def post(self, request):
        serializer = GenerateOtpSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                send_otp_email(user)
                return Response({"message": "OTP sent successfully."})
            except User.DoesNotExist:
                return Response({"message": "User not found."})
        return Response(serializer.errors)

# Utility function to send OTP email
def send_otp_email(user):
    otp = generate_otp()
    user.otp = otp
    user.otp_expiry_time = timezone.now() + timedelta(minutes=5)
    user.save()
    # Send email with OTP

