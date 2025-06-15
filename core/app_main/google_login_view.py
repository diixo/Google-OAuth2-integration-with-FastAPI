
import jwt
from django.contrib.auth import get_user_model, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from django.utils.timezone import now
from django.conf import settings

import logging
import logging as logger

logging.basicConfig(
    level=logging.INFO,  # Set the default logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)


User = get_user_model()

class GoogleLoginView(APIView):
    def post(self, request):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise AuthenticationFailed("JWT token required")

        token = token.split(" ")[1]

        try:
            payload = jwt.decode(
                token,
                settings.FASTAPI_JWT_SECRET,
                algorithms=[settings.FASTAPI_JWT_ALGORITHM]
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        email = payload.get("email")
        if not email:
            raise AuthenticationFailed("No email in token")

        email_name = email.split("@")[0]
        given_name = payload.get("given_name", "")
        family_name  = payload.get("family_name", "")

        # Создаём пользователя на лету (если его ещё нет)
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email_name,
                "first_name": given_name,
                "last_name": family_name
            }
        )

        if created:
            user.username = email_name
            user.first_name = given_name
            user.last_name = family_name
            user.set_unusable_password()
            user.save()

        logger.info(f"User: {email}, first_name={given_name}, last_name={family_name}")

        user.last_login = now()
        user.save()

        login(request, user)

        session_key = request.session.session_key
        if session_key is None:
            raise AuthenticationFailed("Session was not created")

        if request.user.is_authenticated:
            print("Login operation successfully:", request.user)
        else:
            print("Login operation failed")

        return Response({
            "status": "ok",
            "session": session_key,
            "user": {
                "email": user.email,
                "is_authenticated": True
            }
        })
