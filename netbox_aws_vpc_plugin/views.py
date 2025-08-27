from netbox.views import generic

from . import filtersets, forms, models, tables


# VPC Views
class AWSVPCView(generic.ObjectView):
    queryset = models.AWSVPC.objects.all()

    def get_extra_context(self, request, instance):
        table = tables.AWSSubnetTable(instance.awssubnet_set.all())
        table.configure(request)

        return {
            "subnets_table": table,
        }


class AWSVPCListView(generic.ObjectListView):
    queryset = models.AWSVPC.objects.all()
    table = tables.AWSVPCTable
    filterset = filtersets.AWSVPCFilterSet
    filterset_form = forms.AWSVPCFilterForm
    # TODO: Count of subnets


class AWSVPCEditView(generic.ObjectEditView):
    queryset = models.AWSVPC.objects.all()
    form = forms.AWSVPCForm


class AWSVPCDeleteView(generic.ObjectDeleteView):
    queryset = models.AWSVPC.objects.all()


# Subnet Views
class AWSSubnetView(generic.ObjectView):
    queryset = models.AWSSubnet.objects.all()


class AWSSubnetListView(generic.ObjectListView):
    queryset = models.AWSSubnet.objects.all()
    table = tables.AWSSubnetTable
    filterset = filtersets.AWSSubnetFilterSet
    filterset_form = forms.AWSSubnetFilterForm


class AWSSubnetEditView(generic.ObjectEditView):
    queryset = models.AWSSubnet.objects.all()
    form = forms.AWSSubnetForm


class AWSSubnetDeleteView(generic.ObjectDeleteView):
    queryset = models.AWSSubnet.objects.all()


# Account Views
class AWSAccountView(generic.ObjectView):
    queryset = models.AWSAccount.objects.all()

    def get_extra_context(self, request, instance):
        table = tables.AWSVPCTable(instance.awsvpc_set.all())
        table.configure(request)

        return {
            "vpcs_table": table,
        }


class AWSAccountListView(generic.ObjectListView):
    queryset = models.AWSAccount.objects.all()
    table = tables.AWSAccountTable


class AWSAccountEditView(generic.ObjectEditView):
    queryset = models.AWSAccount.objects.all()
    form = forms.AWSAccountForm


class AWSAccountDeleteView(generic.ObjectDeleteView):
    queryset = models.AWSAccount.objects.all()
