from django.urls    import path
from user.views    import SignUp, SignIn

urlpatterns = [
        path('/signup', SignUp.as_view()),
        path('/signin', SignIn.as_view())
]


