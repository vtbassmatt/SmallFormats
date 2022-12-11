from crawler import views
from django.urls import path


app_name = 'crawler'
urlpatterns = [
    path('', views.crawler_index, name="index"),
    path('logs/', views.log_index, name="log-index"),
    path('logs/<int:start_log>', views.log_from, name="log-from"),
    path('run/<int:run_id>/', views.run_detail, name="run-detail"),
    path('run/<int:run_id>/cancel', views.run_cancel_hx, name="run-cancel"),
    path('run/<int:run_id>/clear', views.run_remove_error_hx, name="run-remove-error"),
    path('run/<int:run_id>/infinite', views.run_remove_limit_hx, name="run-remove-limit"),
    path('stats/', views.update_stats, name="update-stats"),
]
