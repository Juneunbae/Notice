# 임원 공지사항

- ERD
<img width=700 alt="스크린샷 2022-08-14 오후 4 47 48" src="https://user-images.githubusercontent.com/96857114/184527532-85b395cb-d125-432a-b6a1-5a578add0a49.png">

```
settings.py

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES' : [
        'rest_framework.authentication.TokenAuthentication',
    ],
}
```
- 인증 방식으로 토큰을 사용하기 위해 settings.py 에 옵션 추가!

```
Serializers.py

class RegisterSerializer(serializers.ModelSerializer) :

    email = serializers.EmailField(
        required = True,
        validators = [UniqueValidator(queryset=User.objects.all())],
        )

    password = serializers.CharField(
        write_only = True,
        required = True,
        validators = [validate_password],
        )

    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta :
        model = User
        fields = ('username', 'password', 'password2', 'email')

    def validate(self, data) :
        if data['password'] != data['password2'] :
            raise serializers.ValidationError(
                {'password' : '비밀번호가 일치하지 않습니다.'}
            )

        return data

    def create(self, validated_data) :
        user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return user
```
회원가입
- Email - UniqueValidator를 이용하여 이메일 중복 방지
- Password - Django의 기본 패스워드 검증 도구인 validate_password를 사용하여 비밀번호에 대한 검증
- validate 함수를 이용하여 password와 password2 일치 여부를 확인한다.
- CREATE 요청에 대해 create 메소드를 오버라이딩하여 유저를 생성하고 토큰을 생성하게 한다.

```
serializers.py

class LoginSerializer(serializers.Serializer) :
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data) :
        user = authenticate(**data)
        if user :
            token = Token.objects.get(user=user)
            return token
        raise serializers.ValidationError(
            {'error' : '유효하지 않은 회원정보 입니다.'}
        )
```
로그인
- Django의 기본 authenticate 함수, 우리가 설정한 토큰 인증 방식으로 유저를 인증해준다.
- password 옵션에 write_only값을 True로 설정하여, 서버에서 클라이언트에게 json 형태로 불가능하게 설정하여 비밀번호 유출 막기!
- validate 함수를 사용하여 사용자를 인증하여 토큰을 발급하거나, 오류 발생

```
class Profile(models.Model) :
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    fullname = models.CharField(max_length=10)
    image = models.ImageField(upload_to='profile/', default='default.png')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs) :
    if created :
        Profile.objects.create(user=instance)
```
프로필 모델
- OneToOneField로 User와 1:1로 연결되는 새로운 모델을 하나 만드는 방식으로 프로필을 만듭니다.
- @receiver로 시작하는 create_user_profile 함수는 User 모델이 post_save 이벤트를 발생시켰을 때, 해당 User와 연결되는 프로필 데이터를 생성합니다.
- @receiver를 선언해줌으로써 프로필을 생성해 주는 코드를 직접 작성하지 않아도 이벤트를 감지해 자동으로 생성할 수 있습니다.

```
permissions.py

class CustomReadOnly(permissions.BasePermission) :
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS :
            return True
        return obj.user == request.user
```
- 프로필 전체를 건드리는 요청이 없고, 각 객체에 대한 요청이 있으므로 has_object_permissions 메소드를 가져와서 작성한다.
- permissions.SAFE_METHODS 라는 것은 데이터에 영향을 미치지 않는 메소드 즉, GET 을 의미한다.
- GET 요청은 True로 반환하여 통과시키고, PUT/PATCH와 같은 데이터에 영향을 미치는 경우 요청으로 들어온 유저와 객체 유저를 비교하여 같으면 통과시킨다.

```
class Post(models.Model) :
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True)
    title = models.CharField(max_length=128)
    category = models.CharField(max_length=128)
    body = models.TextField()
    image = models.ImageField(upload_to='post/', null=True, blank=True)
    likes = models.ManyToManyField(User, related_name='like_posts', blank=True)
    published_date = models.DateTimeField(default=timezone.now)

    def get_category(self, obj):
       return [category.name for category in obj.category.all()]
```
공지사항 모델
- 글쓴이, 글쓴이 프로필, 제목, 카테고리, 내용, 이미지, 좋아요, 만든 날짜 순으로 작성
- 카테고리를 리스트 형태로 가져오기 위해 get_category 라는 함수를 추가

```
permissions.py

class CustomReadOnly(permissions.BasePermission) :
    def has_permission(self, request, view):
        if request.method == 'GET' :
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS :
            return True
        return obj.author == request.user
```
- 공지사항 글 조회는 가입하지 않은 유저도 가능하지만, 게시글을 생성할 수 있는 권한은 인증된 유저만 가능하며, 해당 게시글 수정/삭제의 권한은 글을 쓴 작성자만 가능한 일이다.
- def has_permission 함수는 GET 방식의 글 조회는 True 값으로 리턴하여 허용하지만, 생성하는 것은 인증된 유저만 가능하게 할 수 있게 리턴 값에 request.user.is_authenticated를 선언
- def has_object_permission 함수는 SAFE_METHODS 즉, GET 방식은 True로 리턴하지만, 수정/삭제는 글을 쓴 유저만 가능하므로 obj.author == request.user 로 선언 

```
class Comment(models.Model) :
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
```
댓글 모델
- 글쓴이, 글쓴이 프로필, 댓글 작성할 게시물, 댓글의 내용으로 구성

```
views.py

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def like_post(request, pk) :
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.likes.all() :
        post.likes.remove(request.user)
        messages = {
            'Delete' : '좋아요 삭제'
        }
        return Response(messages, {'status' : 'ok'})
    else :
        post.likes.add(request.user)
        messages = {
            'Add' : '좋아요'
        }
        return Response(messages, {'status' : 'ok'})
```
좋아요
- 데코레이터를 이용하여 GET 요청을 받는 함수형 뷰라는 설정과 permission을 IsAuthenticated로 선언하여 인증된 유저만 기능이 가능하게 설정
- get_objects_or_404로 해당 글이 없을 시, 404 에러 발생
- 게시글의 모든 좋아요를 누른 유저안에 요청을 보낸 유저가 없을 시, 좋아요 추가! 유저가 있을 시에는 좋아요 삭제!
