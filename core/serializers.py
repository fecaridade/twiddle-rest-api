from rest_framework import serializers
from core.models import Profile,Posts


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    followers = serializers.SerializerMethodField('get_followers')
    profile_photo = serializers.ImageField(max_length=None,use_url=True)
    def get_followers(self,instance):
        follows = list()
        ins = instance.follows.get_queryset()
        for i in ins:
            follows.append(i.user.username)
        return follows

    class Meta:
        model = Profile
        fields = ['username','followers','profile_photo']


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ['tittle','post','created']

class ProfilePhotoSerializer(serializers.Serializer):
    profile_photo = serializers.ImageField()

    def validate_profile_photo(self, value):
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("maximum size is 10 MB")
        return value

    def update(self, instance, validated_data):
        instance.profile_photo = validated_data['profile_photo']
        instance.save()
        return instance
