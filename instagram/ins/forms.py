import django_filters as filters

from django.contrib.auth import get_user_model

from ins.models import Ins

User = get_user_model()


class UserFilter(filters.FilterSet):
    created_at_min = filters.DateFilter(name='created_at', lookup_expr='gte')
    created_at_max = filters.DateFilter(name='created_at', lookup_expr='lte')

    class Meta:
        model = User
        fields = ('created_at_min', 'created_at_max', 'level')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InsFilter(filters.FilterSet):
    created_at_min = filters.DateFilter(name='created_at', lookup_expr='gte')
    created_at_max = filters.DateFilter(name='created_at', lookup_expr='lte')

    class Meta:
        model = Ins
        fields = ('created_at_min', 'created_at_max', 'type')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
