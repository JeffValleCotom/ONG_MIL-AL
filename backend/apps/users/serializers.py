from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth.models import Group
from .roles import INSTITUTIONAL_ROLES
from django.contrib.auth import authenticate, get_user_model


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para la consulta, creación y actualización
    de usuarios institucionales de MIL-AL.

    La contraseña es únicamente de escritura y utiliza
    los validadores y mecanismos de hashing de Django.
    """
    
    roles = serializers.SlugRelatedField(
        source="groups",
        many=True,
        read_only=True,
        slug_field="name",
    )
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
            "roles",
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

class UserRoleAssignmentSerializer(serializers.Serializer):
    roles = serializers.ListField(
        child=serializers.ChoiceField(
            choices=INSTITUTIONAL_ROLES,
        ),
        allow_empty=True,
    )

    def validate_roles(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "No se permiten roles duplicados."
            )

        existing_roles = set(
            Group.objects.filter(
                name__in=value
            ).values_list("name", flat=True)
        )

        missing_roles = set(value) - existing_roles

        if missing_roles:
            raise serializers.ValidationError(
                "Existen roles institucionales que no están "
                "registrados en la base de datos."
            )

        return value

    def update(self, instance, validated_data):
        role_names = validated_data["roles"]

        groups = Group.objects.filter(
            name__in=role_names
        )

        instance.groups.set(groups)

        return instance

class LoginSerializer(serializers.Serializer):
    """
    Valida las credenciales de un usuario institucional.

    Esta clase únicamente verifica usuario y contraseña.
    La creación de la sesión corresponde a TASK-10.
    """

    username = serializers.CharField(
        max_length=150,
        required=True,
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["username"],
            password=attrs["password"],
        )

        if user is None:
            raise serializers.ValidationError(
                "Credenciales inválidas."
            )

        return {
            "user": user,
        }

class UserProfileSerializer(serializers.ModelSerializer):

    roles = serializers.SlugRelatedField(
        source="groups",
        many=True,
        read_only=True,
        slug_field="name",
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "roles",
            "is_active",
            "date_joined",
            "last_login",
        ]

        read_only_fields = [
            "id",
            "username",
            "roles",
            "is_active",
            "date_joined",
            "last_login",
        ]