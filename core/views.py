from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import Profile,Posts
from core.serializers import ProfileSerializer,PostSerializer
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from utils import CustomPagination
import os
import uuid
import random
from twiddle.storage_backend import MediaStoragePublico
from django.core.files.storage import default_storage
from django.conf import settings

class ProfileListView(APIView):
    '''
    Mostra os posts de todos os perfis

    Método: GET
    Endpoint: /posts/
    Retorno: Retorna os posts dos perfis
    '''
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profiles = Profile.objects.all().exclude(id=request.user.id)
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)


class ProfileDetailView(APIView):
    '''
        Mostra os detalhes de um perfil específico.

        Método: GET
        Endpoint: /profiles/<int:pk>/
        Parâmetros de URL: pk (ID do perfil)
        Retorno: Retorna os detalhes do perfil especificado.
    '''

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request,pk):
        profiles = Profile.objects.get(pk=pk)
        serializer = ProfileSerializer(profiles)
        return Response(serializer.data)


class CreateUserView(APIView):
    '''
    Cria um novo usuário e perfil associado.

    Método: POST
    Endpoint: /users/
    Parâmetros:
        username (string): Nome de usuário do novo usuário.
        password (string): Senha do novo usuário.
        email (string): Email do novo usuário.
    Retorno: Retorna os detalhes do perfil recém-criado.
    '''

    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        email = request.data.get('email', '')
        if User.objects.filter(username=username).exists():
            return Response({'message': 'Username already exists.'}, status=400)
        user = User.objects.create_user(username=username, password=password,email=email)
        profile = Profile.objects.create(user=user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)


class FollowView(APIView):
    '''
    Permite que um usuário siga outro perfil.

    Método: POST
    Endpoint: /profiles/<int:pk>/follow/
    Parâmetros de URL: pk (ID do perfil a ser seguido)
    Retorno: Retorna uma mensagem indicando se o usuário foi seguido com sucesso.
    '''

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        profile = Profile.objects.get(pk=pk)
        user_profile = Profile.objects.filter(user= request.user.id).get()

        if profile.user.id == request.user.id:
            return Response({'message': 'You can´t self follow'})
        if profile in user_profile.follows.all():
            return Response({'message': 'you already follow'})

        user_profile.follows.add(profile)
        return Response({'message': 'Successfully followed.'})


class RecommendedPostView(APIView):
    '''
    Obtém uma lista paginada de posts recomendados para o usuário.

    Método: GET
    Endpoint: /posts/recommended/
    Retorno: Retorna uma lista paginada de posts recomendados para o usuário.
    A ordem dos posts pode ser baseada em um ranking específico, como postagens de pessoas seguidas ou número de curtidas.

    '''

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        paginator = self.pagination_class()
        user = request.user
        posts = Posts.objects.exclude(user=user).order_by('-created')
        paginated_posts = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(paginated_posts, many=True)
        return paginator.get_paginated_response(serializer.data)


class ProfilePostView(APIView):
    '''
    Mostra os posts de um perfil específico.

    Método: GET
    Endpoint: /profiles/<int:pk>/posts/
    Parâmetros de URL: pk (ID do perfil)
    Retorno: Retorna os posts do perfil especificado.

    '''
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request,pk):
        paginator = self.pagination_class()
        posts = Posts.objects.filter(user=pk).order_by('-created')
        paginated_posts = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(paginated_posts, many=True)
        return paginator.get_paginated_response(serializer.data)


class PostListView(APIView):
    '''
    Mostra os posts de todos os perfis seguidos pelo usuário.

    Método: GET
    Endpoint: /posts/
    Retorno: Retorna os posts dos perfis seguidos pelo usuário.
    '''

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        paginator = self.pagination_class()
        profile = Profile.objects.filter(user=request.user.id).get()
        follows = list(profile.follows.select_related('user__user_profile'))
        posts = Posts.objects.filter(user__user_profile__in= follows)
        paginated_posts = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(paginated_posts, many=True)
        return paginator.get_paginated_response(serializer.data)


class PostCreateView(APIView):
    '''
    Cria um novo post.

    Método: POST
    Endpoint: /posts/
    Retorno: Retorna os detalhes do post recém-criado.
    '''

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination


    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save(user=request.user)
            return Response(PostSerializer(post).data, status=201)
        return Response(serializer.errors, status=400)


class ProfilePhotoUploadView(APIView):
    #parser_classes = [FileUploadParser,MultiPartParser]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        file = request.data.get('profile_photo')
        file_extension = os.path.splitext(file.name)[1]
        seed_filename_name = uuid.uuid1(random.randint(0, 281476710))
        file_name = f"profile_photo_{seed_filename_name}_{file_extension}"

        if settings.USE_S3:
            s3_storage = MediaStoragePublico()
            file_path = s3_storage.save(file_name, file)
            profile = request.user.user_profile
            profile.profile_photo = file_path
            profile.save()

        else:
            file_path = default_storage.save(file_name, file)
            profile = request.user.user_profile
            profile.profile_photo = file_path
            profile.save()

        return Response({'message': 'Profile photo uploaded successfully.'})




