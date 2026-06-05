from django.contrib import admin
from django.urls import path, include
from frontend import views  # This is the correct one!
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path("join/", views.join_now, name="join"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/toggle-2fa/", views.toggle_2fa, name="toggle_2fa"),
    path("about/", views.about, name="about"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("terms-and-conditions/", views.terms_conditions, name="terms_conditions"),
    path("refund-policy/", views.refund_policy, name="refund_policy"),
    path("daily-challenge/<int:challenge_id>/", views.daily_challenge_record, name="daily_challenge_record"),
    path("daily-challenge/<int:challenge_id>/submit/", views.daily_challenge_submit, name="daily_challenge_submit"),
    path("plans/", views.plans_page, name="plans"),
    path("team/", views.team, name="team"),
    path("team/video/<int:submission_id>/comment/", views.add_challenge_video_comment, name="add_challenge_video_comment"),
    path("team/comments/<int:comment_id>/edit/", views.edit_challenge_video_comment, name="edit_challenge_video_comment"),
    path("team/comments/<int:comment_id>/delete/", views.delete_challenge_video_comment, name="delete_challenge_video_comment"),
    path("testimonial/", views.testimonial, name="testimonial"),
    path("add_review/", views.add_review, name="add_review"),
    path("add-success-story/", views.add_success_story, name="add_success_story"),
    path("contact/", views.contact, name="contact"),
    path('success/<int:pk>/', views.success_detail, name='success_detail'),
    path("gallery/", views.gallery, name="gallery"),
    path("gallery/<int:id>/", views.gallery_detail, name="gallery_detail"),
    path("diet/", views.diet, name="diet"),
    path("payment/<str:plan_name>/", views.payment, name="payment"),
    path("payment/", views.payment, name="payment"),
    path('workout/', views.workout_page, name='workout'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('chat-with-ai/', views.chat_with_ai, name='chat_with_ai'),
    path('ai-exercise-video-search/', views.ai_exercise_video_search, name='ai_exercise_video_search'),
    path('exercises/', views.track_workout, name='exercise_library'),
    path('training/', views.training_session, name='training_session'),
    path('live-training/', views.live_training_dashboard, name='live_training_dashboard'),
    path('live-training/book/<int:trainer_id>/', views.book_training_session, name='book_training_session'),
    path('live-training/room/<int:session_id>/', views.live_training_room, name='live_training_room'),
    path('live-training/session/<int:session_id>/active/', views.set_training_session_active, name='set_training_session_active'),
    # Trainer area (trainers use normal website; these pages just add trainer tools)
    path('trainer/', views.trainer_profile, name='trainer_profile'),
    path('trainer/login/', views.trainer_login, name='trainer_login'),
    path('trainer/logout/', views.trainer_logout, name='trainer_logout'),
    path('trainer/slots/create/', views.trainer_create_slot, name='trainer_create_slot'),
    path('trainer/slots/<int:slot_id>/active/', views.trainer_toggle_slot_active, name='trainer_toggle_slot_active'),
    path('trainer/slots/<int:slot_id>/start/', views.trainer_start_session, name='trainer_start_session'),
    path('progress/', views.progress_dashboard, name='progress_tracker'),
    path('update-stats/', views.update_stats, name='update_stats'),
    path('record-workout/', views.record_workout_data, name='record_workout'),
    path('notifications/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/clear/', views.clear_notification, name='clear_notification'),
    path('notifications/clear-all/', views.clear_all_notifications, name='clear_all_notifications'),
    path('notifications/', views.notification_history, name='notification_history'),
    path('save-diet-plan-ai/', views.save_diet_plan_from_ai, name='save_diet_plan_ai'),
    path('delete-diet-plan-ai/', views.delete_diet_plan_ai, name='delete_diet_plan_ai'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
