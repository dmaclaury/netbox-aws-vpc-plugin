from netbox.api.routers import NetBoxRouter

from . import views

app_name = "netbox_aws_vpc_plugin"

router = NetBoxRouter()
router.register("aws-vpcs", views.AWSVPCViewSet)
router.register("aws-subnets", views.AWSSubnetViewSet)
router.register("aws-accounts", views.AWSAccountViewSet)

urlpatterns = router.urls
