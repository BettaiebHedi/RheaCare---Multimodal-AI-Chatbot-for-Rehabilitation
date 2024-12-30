from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.starter_page, name='starter_page'),
    path('index/', views.index_page, name='index_page'),
    # path('chat/', views.chatbot, name='chatbot'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('chat/', views.chatbot, name='index_page3'),
    path('logout/', views.user_logout, name='logout'),  # URL de déconnexion
    path('loader/', views.loader, name='loader'),  # Route vers la page loader
    path('generate-image/', views.generate_image, name='generate_image'),
    path('query/', views.query_documents, name='query_documents'),
    path('rag/', views.generate_rag_response, name='generate_rag_response'),
]
