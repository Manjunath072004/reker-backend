from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Merchant, MerchantBankAccount, MerchantSettings
from .serializers import MerchantSerializer, MerchantBankAccountSerializer, MerchantSettingsSerializer
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class MerchantViewSet(viewsets.ModelViewSet):
    queryset = Merchant.objects.select_related('settings').prefetch_related('bank_accounts').all()
    serializer_class = MerchantSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # merchants should only access their own merchant object
        user = self.request.user
        # if user is staff (admin) show all
        if user.is_staff:
            return super().get_queryset()
        return Merchant.objects.filter(user=user).select_related('settings').prefetch_related('bank_accounts')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        # GET /api/merchants/me/ -> current merchant profile
        merchant = get_object_or_404(Merchant, user=request.user)
        serializer = self.get_serializer(merchant)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def upload_kyc(self, request):
        # simple KYC upload endpoint (file field 'document')
        merchant = get_object_or_404(Merchant, user=request.user)
        f = request.FILES.get('document')
        if not f:
            return Response({'detail': 'No document provided'}, status=status.HTTP_400_BAD_REQUEST)
        # store file (attach to merchantprofile or separate model). For demo, save to disk.
        from django.core.files.storage import default_storage
        path = default_storage.save(f"kyc/{merchant.id}/{f.name}", f)
        # in prod, store metadata in a KYC model and queue verification
        return Response({'detail': 'uploaded', 'path': path}, status=status.HTTP_201_CREATED)
