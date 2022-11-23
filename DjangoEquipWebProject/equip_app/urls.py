from django.urls import path
from .views import EquipmentList, EquipmentDetail, CreateLend, LendList

urlpatterns = [
        path('list/', EquipmentList.as_view(), name ='list'),
        path('detail/<int:pk>', EquipmentDetail.as_view(), name ='detail'),
        path('lend/create/', CreateLend.as_view(), name ='lend_create'),
        path('lend/list/', LendList.as_view(), name ='lend_list'),
    ]