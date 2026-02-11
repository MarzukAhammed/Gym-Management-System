from django.contrib import admin
from django.urls import path
from frontend import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path("join/", views.join_now, name="join"),
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("about/", views.about, name="about"),
    path("plans/", views.plans_page, name="plans"),
    path("team/", views.team, name="team"),
    path("testimonial/", views.testimonial, name="testimonial"),
    path("add_review/", views.add_review, name="add_review"),
    path("contact/", views.contact, name="contact"),
    path('success/<int:pk>/', views.success_detail, name='success_detail'),
    path("gallery/", views.gallery, name="gallery"),
    path("gallery/<int:id>/", views.gallery_detail, name="gallery_detail"),
    path("diet/", views.diet, name="diet"),
    path("payment/", views.payment, name="payment"),
    path("payment/success/", views.payment_success, name="payment_success"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
