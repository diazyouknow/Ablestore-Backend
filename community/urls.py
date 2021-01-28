from django.urls import path
from community.views      import (CategoryBoard,
                                BoardDetail,
                                AddBoardLike,
                                BoardComment,
                                SelfComment,
                                CommentLike,
                                Soluthion,
                                MainBoard,
                                BoardNumber,
                                BoardSearch,
                                Profile,
                                AddHit
                                )


urlpatterns = [
    path('/categories/<int:category_pk>/boards/<int:board_pk>', BoardDetail.as_view()),
    path('/categories/<int:category_pk>/boards', CategoryBoard.as_view()),
    path('/boards/<int:board_pk>/likes', AddBoardLike.as_view()),
    path('/boards/<int:board_pk>/comments', BoardComment.as_view()), # 특정 게시글의 댓글 get, post, delete
    path('/boards/<int:board_pk>/comments/<reply_pk>/comments', SelfComment.as_view()), # 특정 댓글의 댓글 생성 post
    path('/comments/<int:comment_pk>/likes', CommentLike.as_view()),
    path('/boards/<int:board_pk>/comments/<int:comment_pk>', Soluthion.as_view()), #댓글 솔루션 지정
    path('/boards',  MainBoard.as_view()), #용석님 부분 메인 페이지 
    path('/boards/numbers', BoardNumber.as_view()),
    path('/boards/search', BoardSearch.as_view()),
    path('/users/<int:user_pk>/profile', Profile.as_view()),
    path('/categories/<int:category_pk>/boards/<int:board_pk>/hits', AddHit.as_view()),
]

 
