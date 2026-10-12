from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para la consulta, creación y actualización
    de usuarios institucionales de MIL-AL.

    La contraseña es únicamente de escritura y utiliza
    los validadores y mecanismos de hashing de Django.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "is_active",
            "date_joined",
            "last_login",
        ]

        read_only_fields = [
            "id",
            "is_active",
            "date_joined",
            "last_login",
        ]

    def create(self, validated_data):
        """
        Crea un usuario almacenando la contraseña
        mediante el mecanismo seguro de Django.
        """
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user

    def update(self, instance, validated_data):
        """
        Actualiza información del usuario.

        En una actualización parcial, la contraseña es
        opcional. Si se proporciona, se almacena de forma segura.
        """
        password = validated_data.pop("password", None)

        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)

        if password:
            instance.set_password(password)

        instance.save()

        return instance