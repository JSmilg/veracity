from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.claims.views import (
    JournalistViewSet,
    ClaimViewSet,
    ScoreHistoryViewSet,
    TransferViewSet,
    ReferenceClubViewSet,
    ReferencePlayerViewSet,
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'journalists', JournalistViewSet, basename='journalist')
router.register(r'claims', ClaimViewSet, basename='claim')
router.register(r'score-history', ScoreHistoryViewSet, basename='scorehistory')
router.register(r'transfers', TransferViewSet, basename='transfer')
router.register(r'reference-clubs', ReferenceClubViewSet, basename='referenceclub')
router.register(r'reference-players', ReferencePlayerViewSet, basename='referenceplayer')

urlpatterns = [
    path('', include(router.urls)),
]
