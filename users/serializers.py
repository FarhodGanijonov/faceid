from rest_framework import serializers
from .models import FaceComparison, AbstractUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirmation = serializers.CharField(write_only=True)

    class Meta:
        model = AbstractUser
        fields = ['id', 'full_name', 'phone', 'password', 'password_confirmation', 'role']

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError("Parollar bir xil emas.")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirmation')
        user = AbstractUser(
            full_name=validated_data['full_name'],
            phone=validated_data['phone'],
            role=validated_data.get('role', 'Buyer')  # yoki 'Seller' bo‘lishi mumkin
        )
        user.set_password(validated_data['password'])
        user.save()
        return user



class UserLoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone = data.get('phone')
        password = data.get('password')
        user = AbstractUser.objects.filter(phone=phone).first()

        if user and user.check_password(password):
            if not user.is_active:
                raise serializers.ValidationError("Foydalanuvchi faol emas.")
            return user
        raise serializers.ValidationError("Noto‘g‘ri telefon raqam yoki parol.")


class UserPasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Eski parol noto‘g‘ri.")
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError("Yangi parollar bir xil emas.")
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user



class UploadPassportSerializer(serializers.Serializer):
    passport_image = serializers.ImageField()

class UploadFaceSerializer(serializers.Serializer):
    face_image = serializers.ImageField()


# class FaceCompareSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FaceComparison
#         fields = ['passport_image', 'face_image']  # Endi 2 ta rasm keladi


class FaceCompareResponseSerializer(serializers.ModelSerializer):
    passport_image = serializers.SerializerMethodField()
    face_image = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()


    class Meta:
        model = FaceComparison
        fields = ['id', 'passport_image', 'face_image', 'match_result', 'message', 'created_at',]

    def get_passport_image(self, obj):
        request = self.context.get('request')
        if obj.passport_image and hasattr(obj.passport_image, 'url'):
            return request.build_absolute_uri(obj.passport_image.url)
        return None

    def get_face_image(self, obj):
        request = self.context.get('request')
        if obj.face_image and hasattr(obj.face_image, 'url'):
            return request.build_absolute_uri(obj.face_image.url)
        return None

    def get_message(self, obj):
        if obj.match_result:  # Bu True yoki 1 bo‘lsa ham ishlaydi
            return "Ikkala rasm bir odamga tegishli!"
        else:
            return "Bu boshqa odam bo‘lishi mumkin."


class UserContactSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = AbstractUser
        fields = ['id', 'full_name', 'phone', 'gmail', 'telegram', 'image']
        extra_kwargs = {
            'full_name': {'required': False},
            'phone': {'required': False},
            'gmail': {'required': False},
            'telegram': {'required': False},
        }

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url)
        return None

    def update(self, instance, validated_data):
        image_data = self.context.get("request").FILES.get("image")

        if image_data:
            instance.image = image_data

        for field in ['full_name', 'phone', 'gmail', 'telegram']:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        instance.save()
        return instance
