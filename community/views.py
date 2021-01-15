import json 

from django.views import View
from django.http import JsonResponse

from user.utils import login_decorator
from community.models import (Board,
BoardTag,
Category,
Topic,
Tag
)

class BoardView(View):

    @login_decorator
    def post(self, request, category_pk):
        try:
            data     = json.loads(request.body)
            user     = request.user
            category = Category.objects.get(id=category_pk)
            topic    = Topic.objects.get(name=data['topic'])

            board = Board.objects.create(
                category = category,
                topic    = topic,
                user     = user,
                title    = data['title'],
                content  = data['content'],
                image    = data['image']
            )

            if data['tag']: 

                tags = data['tag'].split(',')

                for tag in tags:
                    tag = Tag.objects.get(name=a)

                    BoardTag.objects.create(
                        tag   = tag,
                        board = board
                    )
                    
            return JsonResponse({"MESSAGE":"SUCCESS"}, status=200)

        except KeyError:
            return JsonResponse({"MESSAGE": "KEYERROR"}, status=400)
    
    def get(self, request, category_pk):

        category = Category.objects.get(id=category_pk)
        topic    = request.GET.get("topic",None)
        tags     = request.GET.getlist("tags",None)
        
        boards = Board.objects.select_related(
            'user',
            'topic').prefetch_related(
            'boardtag_set'
            ).filter(category_id=category_pk)

        if topic =="question":
            boards = boards.filter(topic__name="Question")

        if topic =="discussion":
            boards = boards.filter(topic__name="Discussion")
        
        return JsonResponse({"MESSAGE":"SUCCESS"}, status=200)
        
class BoardDetailView(View):

    def get(self, request, category_pk, board_pk): 
        try:
            boards = Board.objects.select_related(
            'user').prefetch_related(
            'boardtag_set'
            ).filter(id=board_pk, category_id=category_pk)

            board     = Board.objects.get(id=board_pk)
            board.hit = board.hit+1
            board.save()

            context = [{
                'id'        : board.id,
                'title'     : board.title,
                'content'   : board.content,
                'created_at': board.created_at,
                'hit'       : board.hit,
            }for board in boards]

            return JsonResponse({"CONTEXT": context}, status=200)

        except ValueError:
            return JsonResponse({'message':'VALUE_ERROR'}, status=400)