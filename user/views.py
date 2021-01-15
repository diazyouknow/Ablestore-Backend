import json, bcrypt, re, jwt

from django.views import View
from django.http import JsonResponse

from .models import User, Country
from my_settings import SECRET_KEY, ALGORITHM

class SignUp(View):
    def post(self, request):
        data           = json.loads(request.body)
        EMAIL_REGEX    = '^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        PASSWORD_REGEX = '^(?=.*[0-9])(?=.*[a-zA-Z]).{8,}$' 
        USER_NAME      = '^[가-힣]{2,4}|[a-zA-Z]{2,10}\s[a-zA-Z]{2,10}$' 
        country        = Country.objects.get(name=data['country'])

        try:
            if not re.match(EMAIL_REGEX, data['email']):
                return JsonResponse({"message":"INVALID_MAIL"},status=400)

            if not re.match(PASSWORD_REGEX, data['password']):
                return JsonResponse({"message":"INVALID_PASSWORD"},status=400)

            if not re.match(USER_NAME, data['name']):
                return JsonResponse({"message":"INVALID_NAME"},status=400)

            if len(data['nickname']) < 2 and len(data['nickname']) > 8:
                return JsonResponse({"message":"INVALID_NICKNAME"},status=400)

            if len(data['code']) < 2 and len(data['code']) > 8:
                return JsonResponse({"message":"INVALID_CODE"},status=400)

            if User.objects.filter(email=data['email']).exists():
                return JsonResponse({"message":"USER_EXIST"}, status=409)

            if User.objects.filter(nickname=data['nickname']).exists():
                return JsonResponse({"message":"NICKNAME_EXIST"},status=409)
            
            if User.objects.filter(code=data['code']).exists():
                return JsonResponse({"message":"CODE_EXIST"}, status=409)

            else:
                User.objects.create(
                    name     = data['name'],
                    country  = country,
                    email    = data['email'],
                    password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode(),
                    nickname = data['nickname'],
                    code     = data['code']
                )

                return JsonResponse({"message":"SUCCESS"},status=201)

        except KeyError:
            return JsonResponse({"message":"KEY_ERROR"},status=401)

class SignIn(View):
    def post(self, request):
        data = json.loads(request.body)
        try:
            user = User.objects.get(email=data['email'])
            if User.objects.filter(email=data['email']).exists():
                
                if bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
                    
                    access_token = jwt.encode({'id':user.id}, SECRET_KEY, ALGORITHM).decode('utf-8')
                    return JsonResponse({"ACCESS_TOKEN": access_token}, status=200)

                return JsonResponse({"message":"INVALID_USER"},status=401)

            return JsonResponse({"message":"INVALID_USER"},status=401)

        except KeyError:
            return JsonResponse({"message":"KEY_ERROR"},status=403)
        except ValueError:
            return JsonResponse({"message":"INVALID_USER"},status=404)