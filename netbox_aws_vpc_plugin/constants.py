from django.db.models import Q

# Q objects for filtering prefixes by IP family
IPV4_PREFIXES = Q(prefix__family=4)
IPV6_PREFIXES = Q(prefix__family=6)
