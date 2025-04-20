from netbox.plugins import PluginMenuButton, PluginMenuItem

vpc_buttons = [
    PluginMenuButton(
        link="plugins:netbox_aws_vpc_plugin:awsvpc_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    )
]

subnet_buttons = [
    PluginMenuButton(
        link="plugins:netbox_aws_vpc_plugin:awssubnet_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    )
]

account_buttons = [
    PluginMenuButton(
        link="plugins:netbox_aws_vpc_plugin:awsaccount_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    )
]

menu_items = (
    PluginMenuItem(
        link="plugins:netbox_aws_vpc_plugin:awsvpc_list",
        link_text="AWS VPCs",
        buttons=vpc_buttons,
    ),
    PluginMenuItem(
        link="plugins:netbox_aws_vpc_plugin:awssubnet_list",
        link_text="AWS Subnets",
        buttons=subnet_buttons,
    ),
    PluginMenuItem(
        link="plugins:netbox_aws_vpc_plugin:awsaccount_list",
        link_text="AWS Accounts",
        buttons=account_buttons,
    ),
)
