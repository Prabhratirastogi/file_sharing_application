from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import File, VerificationToken, User
from django.core.signing import BadSignature
from .utils import send_verification_email
from .serializers import UserSignupSerializer, FileUploadSerializer, FileListSerializer, UserLoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from datetime import timedelta
import uuid
import base64
import json
import logging
from django.http import FileResponse
from rest_framework.permissions import IsAuthenticated

# Logger for tracking events
logger = logging.getLogger(__name__)

class IsClientUser(permissions.BasePermission):
    """
    Custom permission to allow only Client Users to access certain views.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'client_user'


class IsOpsUser(permissions.BasePermission):
    """
    Custom permission to only allow Ops Users to upload files.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'ops_user'


class UserSignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSignupSerializer

    def create(self, request, *args, **kwargs):
        # Validate and save the new user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Automatically verify Ops Users; send verification email to Client Users
        if user.user_type == 'client_user':
            token = str(uuid.uuid4())  # Generate a unique token for email verification
            VerificationToken.objects.create(user=user, token=token)
            send_verification_email(user, token)  # Send verification email

        user.save()
        return Response({
            "message": "User created." + (" Please verify your email." if user.user_type == 'client_user' else "")
        }, status=status.HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer  

    def post(self, request, *args, **kwargs):
        # Validate login credentials
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']  

        # Generate JWT tokens for the logged-in user
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": f"Logged in as {user.user_type.replace('_', ' ').title()}."
        }, status=status.HTTP_200_OK)


class FileUploadView(generics.CreateAPIView):
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.IsAuthenticated, IsOpsUser]  # Restrict access to Ops Users
    authentication_classes = [JWTAuthentication]  # Use JWT for authentication

    def create(self, request, *args, **kwargs):
        # Validate and save the uploaded file
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file_instance = serializer.save(uploaded_by=request.user)  # Save the file instance

        # Prepare response data
        response_data = {
            "message": "File uploaded successfully.",
            "file_name": file_instance.file.name,
            "file_type": file_instance.file.name.split('.')[-1],
            "uploaded_by": request.user.email,
            "upload_date": file_instance.upload_date.strftime("%Y-%m-%d %H:%M:%S"),
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class FileListView(generics.ListAPIView):
    serializer_class = FileListSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can list files
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        
        # Return files based on user type
        if user.user_type == 'ops_user':
            return File.objects.filter(uploaded_by=user)  # Ops Users see their own files
        elif user.user_type == 'client_user' and user.is_verified:
            return File.objects.all()  # Verified Client Users see all files
        
        return File.objects.none()  # If conditions are not met, return no files

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {
            "message": "Files listed successfully",
            "files": response.data  # Include files in the response
        }
        return Response(response.data)


class FileDownloadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # Fetch the file instance based on the primary key
        try:
            instance = File.objects.get(pk=pk)
        except File.DoesNotExist:
            return Response({"error": "File not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is a verified client user
        if request.user.user_type != 'client_user' or not request.user.is_verified:
            return Response({"error": "Only verified Client Users can download files."}, status=status.HTTP_403_FORBIDDEN)

        # Create a dictionary to store the file URL and its expiry time
        data = {
            'file_url': instance.file.url,
            'expiry_time': (timezone.now() + timedelta(minutes=5)).timestamp()  # Set expiry time to 5 minutes
        }

        # Encode the data as a JSON string, then base64-encode it
        signed_url = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()

        return Response({
            'download_link': f'/api/files/download/{signed_url}',  # Return the secure download link
            'message': 'Secure download link generated.'
        }, status=status.HTTP_200_OK)

    def get(self, request, signed_url):
        # Decode the signed URL
        try:
            decoded_data = base64.urlsafe_b64decode(signed_url).decode()
            data = json.loads(decoded_data)

            # Check if the URL has expired
            if timezone.now().timestamp() > data['expiry_time']:
                return Response({"error": "The download link has expired."}, status=status.HTTP_400_BAD_REQUEST)

            # Only allow verified client users to access the file
            if request.user.user_type != 'client_user' or not request.user.is_verified:
                return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)

            # Return the file response for download
            file_path = data['file_url']
            response = FileResponse(open(file_path, 'rb'), as_attachment=True)

            # Set the content disposition to make the file downloadable
            response['Content-Disposition'] = f'attachment; filename="{file_path.split("/")[-1]}"'
            return response

        except (json.JSONDecodeError, ValueError) as e:
            return Response({"error": "Invalid download link."}, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(generics.GenericAPIView):
    def get(self, request, token):
        # Verify the email using the provided token
        try:
            verification_token = VerificationToken.objects.get(token=token)

            # Check if the token has expired
            if verification_token.is_expired():
                logger.info(f"Token {token} has expired for user {verification_token.user.username}.")
                return Response({"error": "Token has expired."}, status=status.HTTP_400_BAD_REQUEST)

            user = verification_token.user
            if not user.is_verified:
                user.is_verified = True  # Mark the user as verified
                user.save()
                verification_token.delete()  # Remove the verification token after use
                logger.info(f"User {user.username} has verified their email successfully.")
                return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)

        except VerificationToken.DoesNotExist:
            return Response({"error": "Invalid verification token."}, status=status.HTTP_400_BAD_REQUEST)
