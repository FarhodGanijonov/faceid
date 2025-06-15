import os

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .serializers import UserPasswordChangeSerializer, \
    UserRegistrationSerializer, UserLoginSerializer, UploadPassportSerializer, UploadFaceSerializer, \
    FaceCompareResponseSerializer
from .models import FaceComparison, AbstractUser
import face_recognition
import numpy as np
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from pillow_heif import register_heif_opener
from rest_framework_simplejwt.tokens import RefreshToken
register_heif_opener()

def resize_image(image, max_size=800):
    image.thumbnail((max_size, max_size), Image.LANCZOS)
    return image

class UploadPassportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UploadPassportSerializer(data=request.data)
        if serializer.is_valid():
            passport_file = serializer.validated_data['passport_image']

            # Save to temp_passport field
            request.user.temp_passport = passport_file
            request.user.save()

            return Response({"message": "Pasport rasmi vaqtincha saqlandi"}, status=200)
        return Response(serializer.errors, status=400)


class CompareFaceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UploadFaceSerializer(data=request.data)
        if serializer.is_valid():
            face_file = serializer.validated_data['face_image']
            passport_file = request.user.temp_passport

            if not passport_file:
                return Response({"error": "Passport rasmi hali yuborilmagan"}, status=400)

            result = self.compare_faces(passport_file, face_file)

            if result is None:
                return Response({"error": "Yuz aniqlanmadi"}, status=400)

            match = result

            # Fayllarni saqlash
            passport_io = BytesIO()
            face_io = BytesIO()

            with Image.open(passport_file) as passport_img:
                passport_img.save(passport_io, format='JPEG')

            with Image.open(face_file) as face_img:
                face_img.save(face_io, format='JPEG')

            passport_content = ContentFile(passport_io.getvalue(), 'passport.jpg')
            face_content = ContentFile(face_io.getvalue(), 'face.jpg')

            comparison = FaceComparison.objects.create(
                user=request.user,
                passport_image=passport_content,
                face_image=face_content,
                match_result=match
            )

            # if request.user.temp_passport and os.path.isfile(request.user.temp_passport.path):
            #     try:
            #         os.remove(request.user.temp_passport.path)
            #     except Exception as e:
            #         print(f"Temp faylni o‘chirishda xatolik: {e}")

            request.user.temp_passport = None
            request.user.save()

            response_serializer = FaceCompareResponseSerializer(comparison, context={"request": request})
            return Response(response_serializer.data, status=200 if match else 400)

        return Response(serializer.errors, status=400)

    def compare_faces(self, passport_file, face_file):
        try:
            with Image.open(passport_file) as passport_img:
                passport_img = resize_image(passport_img)
                passport_array = np.array(passport_img)

            with Image.open(face_file) as face_img:
                face_img = resize_image(face_img)
                face_array = np.array(face_img)

            passport_locations = face_recognition.face_locations(passport_array, model='hog')
            face_locations = face_recognition.face_locations(face_array, model='hog')

            if not passport_locations or not face_locations:
                return None

            passport_enc = face_recognition.face_encodings(passport_array, known_face_locations=passport_locations)
            face_enc = face_recognition.face_encodings(face_array, known_face_locations=face_locations)

            if not passport_enc or not face_enc:
                return None

            match = face_recognition.compare_faces([passport_enc[0]], face_enc[0])[0]
            return match

        except Exception as e:
            print("Face comparison error:", e)
            return None




class UserRegistrationView(generics.CreateAPIView):
    queryset = AbstractUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": self.get_serializer(user).data
        }, status=status.HTTP_201_CREATED)



class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        refresh = RefreshToken.for_user(user)
        refresh['role'] = user.role  # Bu qatorni qoldirsang JWT token ichida "role" field ham bo‘ladi

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserRegistrationSerializer(user).data,
        }, status=status.HTTP_200_OK)


class UserPasswordChangeView(generics.GenericAPIView):
    serializer_class = UserPasswordChangeSerializer
    permission_classes = [IsAuthenticated]  # faqat user roli bo‘lsa

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password updated successfully."})

#rgerger


from .serializers import UserContactSerializer


class UpdateContactView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserContactSerializer(
            request.user, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Kontakt ma'lumotlari yangilandi.", "data": serializer.data})
        return Response(serializer.errors, status=400)


class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = UserContactSerializer(
            user,
            data=request.data,
            partial=True,  # bu yerda `partial=True` bo‘lishi orqali PATCH kabi harakat qiladi
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profil muvaffaqiyatli yangilandi.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]  # faqat token bo‘lsa yetarli

    def get(self, request):
        try:
            # JWT token orqali kelgan user.id ni modelda tekshirish
            user = AbstractUser.objects.get(id=request.user.id)
        except AbstractUser.DoesNotExist:
            return Response({
                "message": "Foydalanuvchi ro‘yxatdan o‘tmagan yoki o‘chirilgan."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = UserContactSerializer(user, context={"request": request})
        return Response({
            "message": "Foydalanuvchi ma'lumotlari muvaffaqiyatli olindi.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout muvaffaqiyatli bajarildi."})
        except Exception as e:
            return Response({"Logout hato bajarildi": str(e)}, status=400)


class ProfileImageDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        delete_flag = str(request.query_params.get("delete", "")).lower()

        if delete_flag not in ["true", "1"]:
            return Response({"message": "`delete=true` query parametri yuborilishi shart."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        if user.image:
            user.image.delete(save=False)
            user.image = None
            user.save()
            return Response({"message": "Profil rasmi o‘chirildi."}, status=status.HTTP_200_OK)

        return Response({"message": "Profil rasmi mavjud emas edi."}, status=status.HTTP_400_BAD_REQUEST)
