# Devflow Auth Service API Documentation

## Overview

The Devflow Auth Service handles user authentication and authorization. This microservice provides endpoints for user registration, login, email verification, password management, and OAuth authentication.

## Base URL

```
/api
```

## Authentication

Protected endpoints require a valid JWT (JSON Web Token). Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints

### User Authentication

#### Register
- **URL**: `/auth/register`
- **Method**: `POST`
- **Description**: Register a new user
- **Authentication**: None
- **Request Body**:
  ```json
  {
    "name": "string",
    "email": "string",
    "password": "string"
  }
  ```
- **Response**:
  - `201 Created`: User registered successfully
    ```json
    {
      "success": true,
      "message": "Registration successful! Please check your email to verify your account."
    }
    ```
  - `400 Bad Request`: Validation error or email already exists

#### Login
- **URL**: `/auth/login`
- **Method**: `POST`
- **Description**: Authenticate a user and receive JWT tokens
- **Authentication**: None
- **Request Body**:
  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```
- **Response**:
  - `200 OK`: Successful login
    ```json
    {
      "success": true,
      "accessToken": "string",
      "refreshToken": "string",
      "user": {
        "_id": "string",
        "name": "string",
        "email": "string",
        "isVerified": boolean
      }
    }
    ```
  - `400 Bad Request`: Invalid credentials
  - `401 Unauthorized`: Email not verified

#### Verify Email
- **URL**: `/auth/verify-email/:token`
- **Method**: `GET`
- **Description**: Verify user's email with token sent to their email
- **Authentication**: None
- **Parameters**:
  - `token`: Email verification token
- **Response**:
  - `200 OK`: Email verified successfully
    ```json
    {
      "success": true,
      "message": "Email verified successfully"
    }
    ```
  - `400 Bad Request`: Invalid or expired token

#### Resend Verification Email
- **URL**: `/auth/resend-verification-email`
- **Method**: `POST`
- **Description**: Resend verification email to user
- **Authentication**: None
- **Request Body**:
  ```json
  {
    "email": "string"
  }
  ```
- **Response**:
  - `200 OK`: Verification email sent
    ```json
    {
      "success": true,
      "message": "Verification email sent"
    }
    ```
  - `400 Bad Request`: Invalid email or user already verified
  - `404 Not Found`: User not found

#### Forgot Password
- **URL**: `/auth/forgot-password`
- **Method**: `POST`
- **Description**: Request password reset link
- **Authentication**: None
- **Request Body**:
  ```json
  {
    "email": "string"
  }
  ```
- **Response**:
  - `200 OK`: Password reset email sent
    ```json
    {
      "success": true,
      "message": "Password reset email sent"
    }
    ```
  - `404 Not Found`: User not found

#### Reset Password
- **URL**: `/auth/reset-password/:token`
- **Method**: `POST`
- **Description**: Reset password using valid token
- **Authentication**: None
- **Parameters**:
  - `token`: Password reset token
- **Request Body**:
  ```json
  {
    "password": "string"
  }
  ```
- **Response**:
  - `200 OK`: Password reset successful
    ```json
    {
      "success": true,
      "message": "Password reset successful"
    }
    ```
  - `400 Bad Request`: Invalid or expired token

#### Change Password
- **URL**: `/auth/change-password`
- **Method**: `POST`
- **Description**: Change user's password
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "currentPassword": "string",
    "newPassword": "string"
  }
  ```
- **Response**:
  - `200 OK`: Password changed successfully
    ```json
    {
      "success": true,
      "message": "Password changed successfully"
    }
    ```
  - `400 Bad Request`: Current password is incorrect
  - `401 Unauthorized`: Authentication required

#### Get Current User
- **URL**: `/auth/me`
- **Method**: `GET`
- **Description**: Get current authenticated user's profile
- **Authentication**: Required
- **Response**:
  - `200 OK`: Returns user profile
    ```json
    {
      "success": true,
      "user": {
        "_id": "string",
        "name": "string",
        "email": "string",
        "isVerified": boolean,
        "createdAt": "string",
        "updatedAt": "string"
      }
    }
    ```
  - `401 Unauthorized`: Authentication required

#### Refresh Token
- **URL**: `/auth/refresh-token`
- **Method**: `POST`
- **Description**: Get new access token using refresh token
- **Authentication**: None
- **Request Body**:
  ```json
  {
    "refreshToken": "string"
  }
  ```
- **Response**:
  - `200 OK`: New access token provided
    ```json
    {
      "success": true,
      "accessToken": "string"
    }
    ```
  - `401 Unauthorized`: Invalid or expired refresh token

#### Logout
- **URL**: `/auth/logout`
- **Method**: `POST`
- **Description**: Invalidate refresh token and log out
- **Authentication**: None
- **Request Body**:
  ```json
  {
    "refreshToken": "string"
  }
  ```
- **Response**:
  - `200 OK`: Logged out successfully
    ```json
    {
      "success": true,
      "message": "Logged out successfully"
    }
    ```
  - `400 Bad Request`: Refresh token is required
  - `401 Unauthorized`: Invalid refresh token



## Error Responses

All endpoints may return these error responses:

- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication failure
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "success": false,
  "message": "Error message"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse. When a rate limit is exceeded, the API returns a `429 Too Many Requests` response.
