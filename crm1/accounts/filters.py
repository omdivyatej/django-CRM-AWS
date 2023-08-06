from .models import *
from  django_filters import *
import django_filters


class OrderFilter(django_filters.FilterSet):
    start_date=DateFilter(field_name="date_created", lookup_expr='gte')
    end_date=DateFilter(field_name="date_created", lookup_expr='lte')    
    
    #product_name = CharFilter(field_name='product', lookup_expr='icontains')
    #does not work for foreign keys from a table.
    class Meta:
        model=Order
        fields = '__all__'
        exclude = ['customer','date_created']