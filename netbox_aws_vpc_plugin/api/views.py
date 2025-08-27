from netbox.api.viewsets import NetBoxModelViewSet

from .. import filtersets, models
from .serializers import AWSAccountSerializer, AWSSubnetSerializer, AWSVPCSerializer


class AWSVPCViewSet(NetBoxModelViewSet):
    queryset = models.AWSVPC.objects.prefetch_related("tags")
    serializer_class = AWSVPCSerializer
    filterset_class = filtersets.AWSVPCFilterSet


class AWSSubnetViewSet(NetBoxModelViewSet):
    queryset = models.AWSSubnet.objects.prefetch_related("tags")
    serializer_class = AWSSubnetSerializer
    filterset_class = filtersets.AWSSubnetFilterSet


class AWSAccountViewSet(NetBoxModelViewSet):
    queryset = models.AWSAccount.objects.prefetch_related("tags")
    serializer_class = AWSAccountSerializer
    filterset_class = filtersets.AWSAccountFilterSet
