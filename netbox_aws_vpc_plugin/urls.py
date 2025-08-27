from django.urls import path
from netbox.views.generic import ObjectChangeLogView

from . import models, views

urlpatterns = (
    # AWS VPC Paths
    path("aws-vpcs/", views.AWSVPCListView.as_view(), name="awsvpc_list"),
    path("aws-vpcs/add/", views.AWSVPCEditView.as_view(), name="awsvpc_add"),
    path("aws-vpcs/<int:pk>/", views.AWSVPCView.as_view(), name="awsvpc"),
    path("aws-vpcs/<int:pk>/edit/", views.AWSVPCEditView.as_view(), name="awsvpc_edit"),
    path("aws-vpcs/<int:pk>/delete/", views.AWSVPCDeleteView.as_view(), name="awsvpc_delete"),
    path(
        "aws-vpcs/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="awsvpc_changelog",
        kwargs={"model": models.AWSVPC},
    ),
    # AWS Subnet Paths
    path("aws-subnets/", views.AWSSubnetListView.as_view(), name="awssubnet_list"),
    path("aws-subnets/add/", views.AWSSubnetEditView.as_view(), name="awssubnet_add"),
    path("aws-subnets/<int:pk>/", views.AWSSubnetView.as_view(), name="awssubnet"),
    path("aws-subnets/<int:pk>/edit/", views.AWSSubnetEditView.as_view(), name="awssubnet_edit"),
    path("aws-subnets/<int:pk>/delete/", views.AWSSubnetDeleteView.as_view(), name="awssubnet_delete"),
    path(
        "aws-subnets/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="awssubnet_changelog",
        kwargs={"model": models.AWSSubnet},
    ),
    # AWS Account Paths
    path("aws-accounts/", views.AWSAccountListView.as_view(), name="awsaccount_list"),
    path("aws-accounts/add/", views.AWSAccountEditView.as_view(), name="awsaccount_add"),
    path("aws-accounts/<int:pk>/", views.AWSAccountView.as_view(), name="awsaccount"),
    path("aws-accounts/<int:pk>/edit/", views.AWSAccountEditView.as_view(), name="awsaccount_edit"),
    path("aws-accounts/<int:pk>/delete/", views.AWSAccountDeleteView.as_view(), name="awsaccount_delete"),
    path(
        "aws-accounts/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="awsaccount_changelog",
        kwargs={"model": models.AWSAccount},
    ),
)
