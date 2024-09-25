from rest_framework import serializers
from .models import User, File
from django.contrib.auth import authenticate

class UserSignupSerializer(serializers.ModelSerializer):
    # Defining the allowable user types for signup
    user_type = serializers.ChoiceField(choices=[('ops_user', 'Ops User'), ('client_user', 'Client User')])

    class Meta:
        model = User  # Specifying the model to serialize
        fields = ['username', 'email', 'password', 'user_type']  # Fields to include in the serialization
        extra_kwargs = {
            'password': {'write_only': True}  # Ensuring password is write-only and not exposed
        }

    def validate(self, data):
        email = data.get('email')
        # Check if a user with the provided email already exists
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(f"A user with the email '{email}' already exists.")
        return data

    def create(self, validated_data):
        # Extract user type from the validated data
        user_type = validated_data.pop('user_type')  
        user = User(
            username=validated_data['username'],  # Setting username
            email=validated_data['email'],        # Setting email
            user_type=user_type                   # Setting user type
        )
        user.set_password(validated_data['password'])  # Hashing the password before saving
        user.save()  # Saving the user instance to the database
        return user

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = File  # Specifying the model to serialize
        fields = ['file']  # Fields to include in the serialization

    def validate_file(self, value):
        # Validate the uploaded file type
        if not value.name.endswith(('.pptx', '.docx', '.xlsx')):  # Allowing only specific file types
            raise serializers.ValidationError("Only .pptx, .docx, and .xlsx files are allowed")
        return value

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)  # Login using email
    password = serializers.CharField(required=True, write_only=True)  # Password is write-only

    def validate(self, attrs):
        # Authenticate the user with the provided email and password
        user = authenticate(username=attrs['email'], password=attrs['password'])  
        if user is None:
            raise serializers.ValidationError("Invalid email or password.")
        
        if not user.is_verified:
            # Ensure the user has verified their email before allowing login
            raise serializers.ValidationError("Please verify your email before logging in.")
        
        attrs['user'] = user  # Attach the authenticated user to the attributes
        return attrs

class FileListSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()  # Display the uploader's email instead of ID

    class Meta:
        model = File  # Specifying the model to serialize
        fields = ['id', 'file', 'uploaded_by', 'upload_date']  # Fields to return in serialization

class FileDownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = File  # Specifying the model to serialize
        fields = ['id', 'file', 'uploaded_by', 'upload_date']  # Fields to return in serialization
