import json 

from django.views import View
from django.http import JsonResponse
from django.db.models import Q
from django.db import transaction
from django.db.models import Count

from datetime import datetime
from user.utils import login_decorator
from user.models import User
from community.models import (Board,
BoardTag,
BoardLike,
Category,
Topic,
Tag,
Comment,
CommentLike
)

class CategoryBoard(View):

    @login_decorator
    def post(self, request, category_pk):
        try:
            data     = json.loads(request.body)
            user     = request.user
            category = Category.objects.get(id=category_pk)
            topic    = Topic.objects.get(name=data['Topic'])

            board = Board.objects.create(
                category = category,
                topic    = topic,
                user     = user,
                title    = data['Title'],
                content  = data['Content'],
                image    = data['Image']
            )

            if data['Tags']: 

                tags = data['Tags'].split(',')

                for tag in tags:
                    tag = Tag.objects.get(name=tag)

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
        limit    = int(request.GET.get("limit",10))
        offset   = int(request.GET.get("offset",0))
        sort     = request.GET.get("sort","updated_time")
        
        q = Q()
        if category:
            q &= Q(category_id=category_pk)
        if topic:
            q &= Q(topic=topic)
        if tags:
            q &= Q(boardtag__tag__in=tags)
        
        boards = Board.objects.select_related(
               'user',
               'topic').prefetch_related(
               'boardtag_set',
               'boardlike_set',
               'comment_set'
               ).filter(q)
        
        if sort =='updated_time':
            boards = Board.objects.select_related(
                'user',
                'category',
                'topic').prefetch_related(
                'boardtag_set',
                'boardlike_set',
                'comment_set'
                ).filter(q).order_by('-created_at')
      
        if sort =='like':
            boards = boards.annotate(num_like=Count('boardlike')).order_by('-num_like')
        #boards = boards.annotate(num_like=Count('boardlike')).order_by('-num_like')
       
        context = [{
                'user_id'       : board.user.id,
                'user_nickname' : board.user.nickname,
                'board_id'      : board.id,
                'category'      : board.category.name,
                'category_id'   : board.category.id,
                'title'         : board.title,
                'solution'      : board.solution,
                'content'       : board.content,
                'created_at'    : board.created_at,
                'hit'           : board.hit,
                'like'          : board.boardlike_set.count(),
                'comment_number': board.comment_set.count(),
                'topic'         : board.topic.name,
                'coment_last'   : MainBoard.check_comment(self, board.id),
                'tags'          : [{"id":board.tag.id,"name":board.tag.name}               
                 for board in board.boardtag_set.all()]
            }for board in boards[offset:offset+limit]]

        
        return JsonResponse({"CONTEXT": context}, status=200)

class AddHit(View):

    def get(self, request, category_pk, board_pk):
        try:
            board     = Board.objects.get(id=board_pk)
            board.hit = board.hit+1
            board.save()

            return JsonResponse({'MESSAGE':"SUCESS_HIT"}, status=200)

        except Board.DoesNotExist:
            
            return JsonResponse({'MESSAGE':'BOARD_NOT_FOUND'},status=404)

class BoardDetail(View):

    def get(self, request, category_pk, board_pk): 
        try:
            boards = Board.objects.select_related(
            'user',
            'topic').prefetch_related(
            'boardtag_set',
            'boardlike_set'
            ).filter(id=board_pk, category_id=category_pk)

            context = [{
                'board_id'  : board.id,
                'title'     : board.title,
                'content'   : board.content,
                'created_at': board.created_at,
                'hit'       : board.hit,
                'topic'     : board.topic.name,
                'user_id'   : board.user.id,
                'nickname'  : board.user.nickname,
                'code'      : board.user.code,
                'like'      : board.boardlike_set.count(),
                'tags'      : [board.tag.name               
                for board in board.boardtag_set.all()]
            }for board in boards]

            if context == []:
                return JsonResponse({'MESSAGE':'BOARD_NOT_FOUND'},status=404)

            return JsonResponse({'CONTEXT': context}, status=200)

        except ValueError:
            return JsonResponse({'MESSAGE':'VALUE_ERROR'}, status=400)
        except KeyError:
            return JsonResponse({'MESSAGE' :'KEY_ERROR'}, status = 400)
        except Board.DoesNotExist:
            return JsonResponse({'MESSAGE':'BOARD_NOT_FOUND'},status=404)
        
    @login_decorator
    def delete(self, request, category_pk, board_pk):
        try:
           user  = request.user
           board = Board.objects.get(id=board_pk, user=user)
           board.delete()
           return JsonResponse({"MESSAGE":"DELETE_SUCCESSFULLY"},status=200)

        except Board.DoesNotExist:
            return JsonResponse({"MESSAGE":"BOARD_NOT_FOUND"},status=404)
    
    @login_decorator
    def put(self, request, category_pk, board_pk):
        try:
            data      = json.loads(request.body)
            user      = request.user
            board     = Board.objects.filter(id=board_pk, user=user)
            board_tag = BoardTag.objects.filter(board_id=board_pk)

            if not board.exists():
                return JsonResponse({"MESSAGE":"USER_NOT_FOUND"},status=404)
            
            topic = Topic.objects.get(name=data['Topic'])
 
            board.update(
             title    = data['Title'],
             content  = data['Content'],
             image    = data['Image']
            )

            if data['Tags']: 

                board_tag.delete()
                tags = data['Tags'].split(',')
                
                for tag in tags:
                    tag = Tag.objects.get(name=tag)

                    board_tag.create(
                        tag   = tag,
                        board_id = board_pk
                    )

            return JsonResponse({"MESSAGE":"MODIFY_SUCCESSFULLY"},status=200)

        except Board.DoesNotExist:
            return JsonResponse({"MESSAGE":"BOARD_NOT_FOUND"},status=404)
    
class AddBoardLike(View):

    @login_decorator
    def post(self, request, board_pk):
        try:
            user  = request.user
            
            if BoardLike.objects.filter(board_id=board_pk, user_id=user.id).exists():
                BoardLike.objects.filter(board_id=board_pk, user_id=user.id).delete()

                return JsonResponse({'MESSAGE': 'BOARD_LIKE_DELETE'}, status=200)

            else:
                BoardLike.objects.create(
                    user_id  = user.id,
                    board_id = board_pk
                )

                return JsonResponse({'MESSAGE': 'BOARD_LIKE_CREATE'}, status=200)

        except ValueError:
            return JsonResponse({'MESSAGE':'VALUE_ERROR'}, status=400)
        except KeyError:
            return JsonResponse({'MESSAGE':'KEY_ERROR'}, status = 400)
        except Board.DoesNotExist:
            return JsonResponse({'MESSAGE':'BOARD_NOT_FOUND'},status=404)

class BoardComment(View):

    def get(self, request, board_pk):
        try:
            
            comments = Comment.objects.filter(board_id=board_pk).select_related("user").order_by('created_at')
            
            context = [{
                'id'        : comment.id,
                'nickname'  : comment.user.nickname,
                'code'      : comment.user.code,
                'content'   : comment.content,
                'created_at': comment.created_at,
                'solution'  : comment.solution,
                'reply'     : comment.reply_id
            }for comment in comments]
           
            return JsonResponse({'CONTEXT':context}, status=200)

        except Comment.DoesNotExist:
            return JsonResponse({'MESSAGE':'COMMENT_NOT_FOUND'}, status = 404)
        except ValueError:
            return JsonResponse({'MESSAGE':'VALUE_ERROR'}, status=400)
        except KeyError:
            return JsonResponse({'MESSAGE':'KEY_ERROR'}, status = 400)

    @login_decorator
    def post(self, request, board_pk):
        try:
            data  = json.loads(request.body)
            user  = request.user
            board = Board.objects.get(id=board_pk)

            if data['content']=="":
                return JsonResponse({'MESSAGE':'EMPTY_CONTENT'})
            else:
                Comment.objects.create(
                    user_id  = user.id,
                    board_id = board_pk,
                    content  = data['content']
                )

            return JsonResponse({'MESSAGE': 'COMMENT_CREATE'}, status=200)

        except ValueError:
            return JsonResponse({'MESSAGE':'VALUE_ERROR'}, status=400)
        except KeyError:
            return JsonResponse({'MESSAGE':'KEY_ERROR'}, status = 400)
        except Board.DoesNotExist:
            return JsonResponse({'MESSAGE':'BOARD_NOT_FOUND'}, status = 404)

    @login_decorator
    def delete(self, request, board_pk):
        try:
           user    = request.user
           data    = json.loads(request.body)
           comment = Comment.objects.get(id=data['comment_id'], user_id=user.id)
           
           comment.delete()
           return JsonResponse({"MESSAGE":"DELETE_SUCCESSFULLY"},status=200)

        except Comment.DoesNotExist:
            return JsonResponse({"MESSAGE":"COMMENT_NOT_FOUND"},status=404)


class SelfComment(View):

    @login_decorator
    def post(self, request, board_pk, reply_pk):
        try:
            data  = json.loads(request.body)
            user  = request.user
            board = Board.objects.get(id=board_pk)

            if data['content']=="":
                return JsonResponse({'MESSAGE':'EMPTY_CONTENT'})
            else:
                Comment.objects.create(
                    user_id  = user.id,
                    board    = board,
                    content  = data['content'],
                    reply_id = reply_pk
                )

            return JsonResponse({'MESSAGE': 'SELF_COMMENT_CREATE'}, status=200)

        except ValueError:
            return JsonResponse({'MESSAGE':'VALUE_ERROR'}, status=400)
        except KeyError:
            return JsonResponse({'MESSAGE':'KEY_ERROR'}, status = 400)
        except Board.DoesNotExist:
            return JsonResponse({'MESSAGE':'BOARD_NOT_FOUND'}, status = 404)

class CommentLike(View):

    @login_decorator
    def post(self, request, comment_pk):
        try:
            user  = request.user
            
            if CommentLike.objects.filter(comment_id=comment_pk, user_id=user.id).exists():
                CommentLike.objects.filter(comment_id=comment_pk, user_id=user.id).delete()

                return JsonResponse({'MESSAGE': 'COMMENT_LIKE_DELETE'}, status=200)
            
            else:
                CommentLike.objects.create(
                    user_id  = user.id,
                    comment_id = comment_pk
                )

                return JsonResponse({'MESSAGE': 'COMMENT_LIKE_CREATE'}, status=200)

        except ValueError:
            return JsonResponse({'MESSAGE':'VALUE_ERROR'}, status=400)
        except KeyError:
            return JsonResponse({'MESSAGE':'KEY_ERROR'}, status = 400)
        except Comment.DoesNotExist:
            return JsonResponse({'MESSAGE':'COMMENT_NOT_FOUND'},status=404)

class Soluthion(View):

    @login_decorator
    def post(self, request, board_pk, comment_pk):
        try:
            user  = request.user
           
            board   = Board.objects.get(id=board_pk, user_id=user.id, topic_id=1)
            comment = Comment.objects.get(id=comment_pk)

            with transaction.atomic():
                board.solution = True
                board.save()

                comment.solution = True
                comment.save()

            
            return JsonResponse({'MESSAGE': 'SOLLUTION_SUCCESS'}, status=200)

        except ValueError:
            return JsonResponse({'MESSAGE':'VALUE_ERROR'}, status=400)
        except KeyError:
            return JsonResponse({'MESSAGE':'KEY_ERROR'}, status = 400)
        except Board.DoesNotExist:
            return JsonResponse({'MESSAGE':'BOARD_NOT_FOUND'},status=404)
                
class MainBoard(View):
    def check_comment(self, board_pk):
        
       if Comment.objects.filter(board_id = board_pk).exists(): 
           data = Comment.objects.filter(board_id = board_pk).order_by('-created_at').first()
           comment_data = {
               "id"            : data.id,
               "user_id"       : data.user.id,
               "nickname"      : data.user.nickname,
               "profile_image" : data.user.profile_image,
               "content"       : data.content,
           }
       else:
           comment_data = {'Message':'THEARE_ARE_NO_COMMENTS'}
       return comment_data

    def get(self, request):
        boards = Board.objects.select_related(
            'user',
            'topic',
            'category').prefetch_related(
            'boardtag_set',
            'boardlike_set',
            'comment_set'
            ).all().order_by('-created_at')
        
        context = [{
                'user_id'       : board.user.id,
                'user_nickname' : board.user.nickname,
                'board_id'      : board.id,
                'category'      : board.category.name,
                'category_id'   : board.category.id,
                'title'         : board.title,
                'solution'      : board.solution,
                'content'       : board.content,
                'created_at'    : board.created_at,
                'hit'           : board.hit,
                'like'          : board.boardlike_set.count(),
                'comment_number': board.comment_set.count(),
                'topic'         : board.topic.name,
                'coment_last'   : MainBoard.check_comment(self, board.id),
                'tags'          : [{"id":board.tag.id,"name":board.tag.name}               
                 for board in board.boardtag_set.all()]
            }for board in boards]

        return JsonResponse({"CONTEXT": context}, status=200)
        
class BoardNumber(View):

    def get(self, request):
        
        total_boards = Board.objects.all()
        
        today = datetime.now().strftime('20%y-%m-%d 00:00')
        
        today_boards = Board.objects.filter(created_at__gt=today)
        
        context = [
            {"id":1, 'count_title': "Today's Posts", 'count_number': today_boards.count()},
            {"id":2, 'count_title': "Total Posts", 'count_number': total_boards.count()}
        ]

        return JsonResponse({"CONTEXT": context}, status=200)

class BoardSearch(View):

    def get(self, request):
        try:
            limit    = int(request.GET.get("limit",10))
            offset   = int(request.GET.get("offset",0))
            query = request.GET.get('query',None)

            boards = Board.objects.select_related(
                'user',
                'topic',
                'category').prefetch_related(
                'boardtag_set',
                'boardlike_set',
                'comment_set'
                ).filter(content__icontains=query)

            comments = Comment.objects.select_related(
                'user',
                'board',
                'board__topic',
                'board__category').prefetch_related(
                'board__boardtag_set',
                'board__boardlike_set'
                ).filter(content__icontains=query)

            if boards or comments:

                board_context = [{
                    'user_id'       : board.user.id,
                    'user_nickname' : board.user.nickname,
                    'board_id'      : board.id,
                    'category'      : board.category.name,
                    'title'         : board.title,
                    'solution'      : board.solution,
                    'board_content' : board.content,
                    'created_at'    : board.created_at,
                    'hit'           : board.hit,
                    'like'          : board.boardlike_set.count(),
                    'comment_number': board.comment_set.count(),
                    'topic'         : board.topic.name,
                    'tags'          : [{"id":boardtag.tag.id,"name":boardtag.tag.name}               
                    for boardtag in board.boardtag_set.all()]
                }for board in boards[offset:offset+limit]]
                
                comment_context = [{
                    'user_id': comment.user.id,
                    'user_nickname' : comment.user.nickname,
                    'board_id'      : comment.board.id,
                    'category'      : comment.board.category.name,
                    'title'         : "Re: "+comment.board.title,
                    'solution'      : comment.board.solution,
                    'comment_content': comment.content ,
                    'created_at'    : comment.board.created_at,
                    'hit'           : comment.board.hit,
                    'like'          : comment.board.boardlike_set.count(),
                    'comment_number': comment.board.comment_set.count(),
                    'topic'         : comment.board.topic.name,
                    'tags'          : [{"id":boardtag.tag.id,"name":boardtag.tag.name}
                    for boardtag in comment.board.boardtag_set.all()]
                }for comment in comments[offset:offset+limit]]
               
                return JsonResponse({"게시글": board_context, "댓글":comment_context}, status=200)

        except Board.DoesNotExist:
            return JsonResponse({'MESSAGE':'BOARD_NOT_FOUND'},status=404)
        except Comment.DoesNotExist:
            return JsonResponse({'MESSAGE':'COMMENT_NOT_FOUND'},status=404)
        except ValueError:
            return JsonResponse({'MESSAGE':'VALUE_ERROR'}, status=400)
        except KeyError:
            return JsonResponse({'MESSAGE':'KEY_ERROR'}, status = 400)
    

class Profile(View):
    
    def get(self, request, user_pk):
        try:
            boards = Board.objects.select_related(
                'user',
                'topic').prefetch_related(
                'boardtag_set',
                'boardlike_set',
                'comment_set'
                ).filter(user_id=user_pk)

            user = User.objects.get(id=user_pk)

            context = [{
                    'board_id'      : board.id,
                    'category'      : board.category.name,
                    'category_id'   : board.category.id,
                    'title'         : board.title,
                    'solution'      : board.solution,
                    'content'       : board.content,
                    'created_at'    : board.created_at,
                    'hit'           : board.hit,
                    'like'          : board.boardlike_set.count(),
                    'comment_number': board.comment_set.count(),
                    'topic'         : board.topic.name,
                    'coment_last'   : MainBoard.check_comment(self, board.id),
                    'tags'          : [{"id":board.tag.id,"name":board.tag.name}               
                    for board in board.boardtag_set.all()]
                }for board in boards]

            user_info = {
                'user_nickname':user.nickname,
                'user_code':user.code,
                'board_count':boards.count()
            }
        
            return JsonResponse({"user_info":user_info,"context":context}, status=200)

        except Board.DoesNotExist:
            return JsonResponse({'MESSAGE':'BOARD_NOT_FOUND'},status=404)
        except Comment.DoesNotExist:
            return JsonResponse({'MESSAGE':'COMMENT_NOT_FOUND'},status=404)
        except ValueError:
            return JsonResponse({'MESSAGE':'VALUE_ERROR'}, status=400)
        except KeyError:
            return JsonResponse({'MESSAGE':'KEY_ERROR'}, status = 400)