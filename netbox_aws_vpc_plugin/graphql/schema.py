from typing import List

import strawberry
import strawberry_django

from .types import AWSAccountType, AWSVPCType


@strawberry.type(name="Query")
class NetBoxAWSVPCQuery:
    aws_account: AWSAccountType = strawberry_django.field()
    aws_account_list: List[AWSAccountType] = strawberry_django.field()

    aws_vpc: AWSVPCType = strawberry_django.field()
    aws_vpc_list: List[AWSVPCType] = strawberry_django.field()
