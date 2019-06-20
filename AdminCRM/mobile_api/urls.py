from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import *

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),
    path('', FeedbackList.as_view(), name='feedback_list_view'),

    # path('', MainView.as_view(), name='index'),
    path('news/', NewsList.as_view(), name='news_list_view'),
    path('news/create/', NewsCreate.as_view(), name='news_create'),
    path('news/<int:pk>/detail/', NewsDetail.as_view(), name='news_detail'),
    path('news/<int:pk>/edit/', NewsEdit.as_view(), name='news_edit'),
    path('news/<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),
    path('promotion/', PromotionsList.as_view(), name='promotion_list_view'),
    path('mobile-device/', MobileDeviceList.as_view(), name='mobile_device_list_view'),
    path('mobile-device/<int:pk>/delete/', MobileDeviceDelete.as_view(), name='mobile_device_delete'),
    path('mobile-device/<int:pk>/edit/', MobileDeviceUpdate.as_view(), name='mobile_device_update'),
    path('mobile-device/repair/', MobileDeviceRepair.as_view(), name='mobile_device_repair'),
    path('mobile-device/<int:user>/delete-device/', DeleteSelectMobileDevice.as_view(), name='delete_select_device'),
    # path('feedback/', FeedbackList.as_view(), name='feedback_list_view'),
    path('feedback/<int:pk>/update/', FeedbackUpdate.as_view(), name='feedback_update'),
    path('push/', PushMessageList.as_view(), name='push_list'),
    path('push/create/', PushMessageCreate.as_view(), name='push_create')
]
