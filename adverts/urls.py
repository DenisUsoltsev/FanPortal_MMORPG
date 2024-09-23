from django.urls import path
from django.views.generic import TemplateView

from . import views


urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('adverts/', views.AdvertsList.as_view(), name='posts'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('add_post/', views.AddPost.as_view(), name='add_post'),
    path('post/<slug:post_slug>/', views.ShowPost.as_view(), name='post'),
    path('category/<slug:cat_slug>/', views.ShowCategory.as_view(), name='category'),
    path('edit/<slug:slug>/', views.EditPost.as_view(), name='edit_post'),
    path('delete/<slug:slug>/', views.DeletePost.as_view(), name='delete_post'),
    path('profile/user_posts/', views.UserPosts.as_view(), name='user_posts'),
    path('profile/user_responses/', views.UserResponses.as_view(), name='user_responses'),
    path('response/<int:pk>/', views.ShowResponse.as_view(), name='response'),
    path('add_response/<int:pk>/', views.AddResponse.as_view(), name='add_response'),
    path('edit_response/<int:pk>/', views.EditResponse.as_view(), name='edit_response'),
    path('delete_response/<int:pk>/', views.DeleteResponse.as_view(), name='delete_response'),
    path('category/<slug:cat_slug>/subscribe/', views.SubscribeToCategoryView.as_view(), name='subscribe_to_category'),
    path('category/<slug:cat_slug>/unsubscribe/', views.UnsubscribeFromCategoryView.as_view(),
         name='unsubscribe_from_category'),
]
