from utilities.choices import ChoiceSet

"""
Define the custom status options for AWS accounts
"""


class AWSAccountStatusChoices(ChoiceSet):
    key = "AWSAccount.status"

    STATUS_ACTIVE = "ACTIVE"
    STATUS_INACTIVE = "INACTIVE"
    STATUS_PENDING_ACTIVATION = "PENDING_ACTIVATION"

    CHOICES = [
        (STATUS_ACTIVE, "Active", "green"),
        (STATUS_INACTIVE, "Inactive", "red"),
        (STATUS_PENDING_ACTIVATION, "Pending Activation", "orange"),
    ]
