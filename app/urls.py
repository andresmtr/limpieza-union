
#Imports
from django.urls import path
from app import views
from django.conf.urls import url 


from .views import Beginning,loadFiles


#Import URL
urlpatterns = [

    # path('',Beginning.index.as_view(), name = 'index'),

    path('',Beginning.index, name = 'index'),
    path('cargar/',loadFiles.load, name = 'cargar'),
    # path('union/',union.concat, name = 'union'),

]