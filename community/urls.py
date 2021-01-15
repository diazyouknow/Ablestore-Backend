from django.urls import path
from community.views      import BoardView,BoardDetailView


urlpatterns = [
    path('/categories/<int:category_pk>/posts/<int:board_pk>', BoardDetailView.as_view()),
    path('/categories/<int:category_pk>/posts', BoardView.as_view()), 
]

 
