from typing import Any
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.models import update_last_login

from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.decorators import action
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from apps.auths.serializers.users import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
)
from apps.auths.models import User


ACCESS_TOKEN_HEADER: str = "X-Access-Token"
REFRESH_TOKEN_HEADER: str = "X-Refresh-Token"


class UserViewSet(ViewSet):
    """User ViewSet for handling user-related actions"""

    queryset = User.objects
    # serializer_class = UserBaseSerializer  # fallback?

    @action(
        methods=("POST",),
        detail=False,
        url_path="login",
        url_name="login",
        permission_classes=(AllowAny,),
    )
    def login(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Handle user login"""

        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data.pop("user")

            # update_last_login(None, user)
            # additional query, could add in login serializer

            refresh_token: RefreshToken = RefreshToken.for_user(user)
            access_token: str = str(refresh_token.access_token)
            headers = {
                ACCESS_TOKEN_HEADER: access_token,
                REFRESH_TOKEN_HEADER: str(refresh_token),
            }

            return DRFResponse(
                data=UserDetailSerializer(user).data,
                status=HTTP_200_OK,
                headers=headers,
            )

        return DRFResponse(data=serializer.errors, status=HTTP_400_BAD_REQUEST)

    @action(
        methods=("POST",),
        detail=False,
        url_path="register",
        url_name="register",
        permission_classes=(AllowAny,),
    )
    def register(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Handle user register"""

        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return DRFResponse(
                data=UserDetailSerializer(user).data, status=HTTP_201_CREATED
            )

        return DRFResponse(data=serializer.errors, status=HTTP_400_BAD_REQUEST)

    @action(
        methods=("GET", "PATCH"),
        detail=False,
        url_path="me",
        url_name="me",
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Handle me"""

        if request.method == "PATCH":
            serializer = UserUpdateSerializer(
                instance=request.user, data=request.data, partial=True
            )

            if serializer.is_valid():
                user = serializer.save()
                detail_serializer = UserUpdateSerializer(user)
                return DRFResponse(detail_serializer.data, status=HTTP_200_OK)
            return DRFResponse(serializer.errors, status=HTTP_400_BAD_REQUEST)

        elif request.method == "GET":
            serializer = UserDetailSerializer(request.user)
            return DRFResponse(data=serializer.data, status=HTTP_200_OK)

        return DRFResponse(status=HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    """Custom TokenRefreshView"""

    def post(self, request: DRFRequest, *args, **kwargs) -> DRFResponse:
        response = super().post(request, *args, **kwargs)

        headers = {ACCESS_TOKEN_HEADER: response.data["access"]}

        return DRFResponse(status=HTTP_200_OK, headers=headers)
