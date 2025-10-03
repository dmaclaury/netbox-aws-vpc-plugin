import strawberry_django

from ..models import AWSVPC, AWSAccount


@strawberry_django.type(
    AWSAccount,
    fields="__all__",
)
class AWSAccountType:
    pass


@strawberry_django.type(
    AWSVPC,
    fields="__all__",
)
class AWSVPCType:
    pass
