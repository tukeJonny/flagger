# -*- coding: utf-8 -*-
from django.contrib.auth import authenticate, get_user_model
User = get_user_model()

from rest_framework import serializers

from scoreserver import models, signals


class NoticeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Notice
        fields = ('id', 'title', 'description', 'created_at', 'updated_at')

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = ('id', 'name')

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tag
        fields = ('id', 'name')

class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Team
        fields = ('id', 'name', 'email', 'password', 'score', 'created_at', 'updated_at')
        read_only_fields = ('id', 'score', 'created_at', 'updated_at')
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

    def validate_password(self, password):
        if password is None or len(password) == 0:
            raise serializers.ValidationError("Please specify your team's password")

        return password

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.set_password(validated_data["password"])
        instance.save()

        return instance

class UserSerializer(serializers.ModelSerializer):

    team_name = serializers.CharField(write_only=True, allow_null=False, required=True)
    team_password = serializers.CharField(write_only=True, allow_null=False, required=True)

    class Meta:
        model = models.User
        fields = ('id', 'username', 'password', 'team', 'score', 'created_at', 'updated_at', 'team_name', 'team_password')
        read_only_fields = ('id', 'team', 'score', 'created_at', 'updated_at')
        extra_kwargs = {
            'team_name': {'write_only': True, 'required': False},
            'team_password': {'write_only': True, 'required': False},
            'password': {'write_only': True, 'required': False}
        }

    def validate(self, data):
        try:
            team = models.Team.objects.get(name=data.get("team_name"))
            if not team.check_password(data.get("team_password")):
                raise serializers.ValidationError("A given password is wrong")
        except models.Team.model.DoesNotExist:
            raise serializers.ValidationError("There are no team name matches given team_name")

        data["team"] = team

        return data

    def create(self, validated_data):
        team = validated_data["team"]

        user = User.objects.create(team=team, username=validated_data["username"])
        user.set_password(validated_data["password"])
        user.save()

        return user

class QuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Question
        fields = ('id', 'categories', 'tags', 'title', 'description', 'author', 'solved_cnt')

class SubmitSerializer(serializers.Serializer):
    """フラグ提出シリアライザー"""

    question_id = serializers.IntegerField(required=True)
    flag_str = serializers.CharField(max_length=255, required=True)
