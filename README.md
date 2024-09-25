# Secure File Sharing System

This project implements a secure file-sharing system using Django REST framework. It differentiates between two types of users: **Ops Users** and **Client Users**. Each user type has specific capabilities, ensuring secure file uploads and downloads.

## Features

### User Roles

1. **Ops Users**:
   - Login
   - Upload files (`pptx`, `docx`, `xlsx` file types only)

2. **Client Users**:
   - Sign Up (generates an encrypted URL for email verification)
   - Email Verification
   - Login
   - List all uploaded files
   - Download files (via a secure encrypted URL)

## API Endpoints and Usage

---

### 1. **User Signup** (`POST`)

- **Endpoint**: `/api/signup/`
- **Description**: Registers a new user and sends a verification email with an encrypted link.
- **Request Body**:

    ```json
    {
      "username": "john",
      "email": "prabhrati@gmail.com",
      "password": "123",
      "user_type": "ops_user" // or 'client_user'
    }
    ```

---

### 2. **User Login** (`POST`)

- **Endpoint**: `/api/login/`
- **Description**: Authenticates the user and returns JWT tokens.
- **Request Body**:

    ```json
    {
      "email": "prabhrati17@gmail.com",
      "password": "123"
    }
    ```

- **Response**:

    ```json
    {
      "access": "<JWT_ACCESS_TOKEN>",
      "refresh": "<JWT_REFRESH_TOKEN>"
    }
    ```

---

### 3. **Email Verification** (`GET`)

- **Endpoint**: `/api/email/verify/<token>/`
- **Description**: Verifies the user's email using the token from the verification email.
- **Request Example**:

    ```http
    GET http://localhost:8000/api/email/verify/ab04ff35-273c-4bf7-9e22-4f0044b5c76f/
    ```

- **Response**:

    ```json
    {
      "message": "Email verified successfully!"
    }
    ```

---

### 4. **Refresh Token** (`POST`)

- **Endpoint**: `/api/token/refresh/`
- **Description**: Refreshes the JWT access token.
- **Request Body**:

    ```json
    {
      "refresh": "<REFRESH_TOKEN>"
    }
    ```

- **Response**:

    ```json
    {
      "access": "<NEW_ACCESS_TOKEN>"
    }
    ```

---

### 5. **File Upload** (`POST`)

- **Endpoint**: `/api/upload/`
- **Description**: Allows Ops Users to upload files. Only `pptx`, `docx`, and `xlsx` files are allowed.
- **Request Type**: `multipart/form-data`
- **Request Example**:

    ```multipart/form-data
    file: <file>
    ```

- **Response**:

    ```json
    {
      "message": "File uploaded successfully.",
      "file_url": "http://localhost:8000/uploads/file.pptx",
      "file_name": "file.pptx",
      "file_type": "pptx",
      "uploader": "prabhrati@gmail.com",
      "upload_date": "2024-09-24"
    }
    ```

---

### 6. **List Uploaded Files** (`GET`)

- **Endpoint**: `/api/files/`
- **Description**: Lists all the files uploaded by Ops Users.
- **Response**:

    ```json
    [
      {
        "id": 1,
        "file_name": "file1.pptx",
        "file_url": "http://localhost:8000/uploads/file1.pptx",
        "uploaded_by": "prabhrati@gmail.com",
        "upload_date": "2024-09-24"
      },
      {
        "id": 2,
        "file_name": "file2.docx",
        "file_url": "http://localhost:8000/uploads/file2.docx",
        "uploaded_by": "john@example.com",
        "upload_date": "2024-09-23"
      }
    ]
    ```

---

### 7. **Get Download Link** (`POST`)

- **Endpoint**: `/api/files/<int:pk>/download/`
- **Description**: Generates a secure encrypted download link for the requested file (only accessible by Client Users).
- **Request Example**:

    ```http
    POST http://localhost:8000/api/files/10/download/
    ```

- **Response**:

    ```json
    {
      "download-link": "http://localhost:8000/api/files/download/signed_encrypted_link",
      "message": "success"
    }
    ```

---

### 8. **Secure File Download** (`GET`)

- **Endpoint**: `/api/files/download/<str:signed_url>/`
- **Description**: Allows Client Users to securely download the file using the provided signed URL.
- **Request Example**:

    ```http
    GET http://localhost:8000/api/files/download/signed_encrypted_link/
    ```

- **Response** (If valid):

    ```json
    {
       "message": "File downloaded successfully."
    }
    ```

- **Response** (If invalid or unauthorized):

    ```json
    {
      "error": "You do not have permission to access this file."
    }
    ```

---

## Setup Instructions

# 1. Clone the Repository
git clone <repository-link>
cd file_sharing_system

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Set Up Environment Variables
# Create a .env file in the root directory with the following content:
DJANGO_SECRET_KEY=your_secret_key
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_email_password
# Replace your_secret_key, your_email@gmail.com, and your_email_password with your actual credentials.

# 4. Run Migrations
python manage.py migrate

# 5. Run the server
python manage.py runserver

# 6. Authentication
The project uses JWT for authentication. After login, you need to include the access token in 
the Authorization header as a Bearer token to access protected resources.

Authorization: Bearer <JWT_ACCESS_TOKEN>

# 7. Postman Collection

The Postman collection for testing all APIs is available in the repository as Postman_Dump.json. 
You can import it into Postman for easy testing of all the provided APIs.

# 8. Conclusion

This project demonstrates a secure file-sharing system where:

.. Ops Users can upload specific file types (pptx, docx, xlsx).
.. Client Users can securely download files using encrypted URLs.



### Key Fixes:

1. Code blocks (` ``` `) are closed properly to avoid breaking the format.
2. Headings and descriptions are properly separated for readability.
3. JSON request/response examples are correctly formatted for consistent indentation and readability.

