from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('meus-processos/', views.meus_processos, name='meus_processos'),
    
    # Templates
    path('templates/', views.TemplateProcessoListView.as_view(), name='template_list'),
    path('templates/<int:pk>/', views.TemplateProcessoDetailView.as_view(), name='template_detail'),
    path('templates/novo/', views.TemplateProcessoCreateView.as_view(), name='template_create'),
    path('templates/<int:pk>/editar/', views.TemplateProcessoUpdateView.as_view(), name='template_update'),
    
    # Etapas
    path('templates/<int:template_pk>/etapas/nova/', views.etapa_create, name='etapa_create'),
    path('etapas/<int:pk>/editar/', views.etapa_update, name='etapa_update'),
    
    # Processos
    path('processos/', views.ProcessoListView.as_view(), name='processo_list'),
    path('processos/<int:pk>/', views.ProcessoDetailView.as_view(), name='processo_detail'),
    path('processos/novo/', views.processo_create, name='processo_create'),
    path('processos/<int:pk>/executar/', views.processo_executar_etapa, name='processo_executar'),
    path('processos/<int:pk>/encaminhar/', views.processo_encaminhar, name='processo_encaminhar'),
    
    # Documentos
    path('etapas-executadas/<int:etapa_executada_pk>/documentos/novo/', views.documento_upload, name='documento_upload'),
]
