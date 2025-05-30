from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.serializers.user import (
    AvatarSerializer,
    SubscriptionSerializer,
    SetPasswordSerializer,
    SubscriptionCreateSerializer
)

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    def get_permissions(self):
        authenticated_actions = [
            'me',
            'set_password',
            'avatar',
            'delete_avatar',
            'subscriptions',
            'subscribe',
            'unsubscribe'
        ]
        if self.action in authenticated_actions:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.action in ['avatar', 'delete_avatar']:
            return AvatarSerializer
        if self.action in ['subscriptions', 'subscribe', 'unsubscribe']:
            return SubscriptionSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = self.get_serializer(request.user, data=request.data, partial=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        if request.method == 'DELETE':
            request.user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='subscriptions', permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribed_to__subscriber=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'], url_path='subscribe', permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        target_user = get_object_or_404(User, pk=id)
        serializer = SubscriptionCreateSerializer(
            data={'target': target_user.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_serializer = SubscriptionSerializer(target_user, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        target_user = get_object_or_404(User, pk=id)

        subscription_qs = request.user.subscriptions.filter(target=target_user)
        if not subscription_qs.exists():
            return Response({'errors': 'Вы не подписаны на этого пользователя.'}, status=status.HTTP_400_BAD_REQUEST)

        subscription_qs.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
