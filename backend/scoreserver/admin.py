from django.contrib import admin

from scoreserver import models

# Register your models here.

class NoticeAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.Notice, NoticeAdmin)

class UserAdmin(admin.ModelAdmin):
    model = models.User
    list_display = ('username', 'email', 'is_superuser', 'is_banned', 'is_active', 'created_at', 'updated_at', 'last_login')
    list_filter = ('is_superuser', 'is_banned', 'is_active')
    search_fields = ['username', 'email', 'is_superuser', 'is_banned', 'is_active', 'created_at', 'updated_at', 'last_login']
    exclude = ('password', 'first_name', 'last_name', 'date_joined', 'user_permissions', 'groups')
admin.site.register(models.User, UserAdmin)

class UserInline(admin.TabularInline):
    model = models.User
    list_display = ('username', 'email', 'is_superuser', 'is_banned', 'is_active', 'created_at', 'updated_at', 'last_login')
    exclude = ('password', 'first_name', 'last_name', 'date_joined', 'user_permissions', 'groups')

class TeamAdmin(admin.ModelAdmin):
    inlines = [UserInline]
admin.site.register(models.Team, TeamAdmin)

class FlagInline(admin.TabularInline):
    model = models.Flag
    extra = 1

class HintInline(admin.TabularInline):
    model = models.Hint
    extra = 1

class TagInline(admin.TabularInline):
    model = models.Question.tags.through
    extra = 1

class CategoryInline(admin.TabularInline):
    model = models.Question.categories.through
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title','description','author','is_public', 'tag_csv','category_csv')
    exclude = ('categories', 'tags')
    inlines = [TagInline,CategoryInline,FlagInline,HintInline]

    def tag_csv(self, row):
        return ','.join([tag.name for tag in row.tags.all()])

    def category_csv(self, row):
        return ','.join([category.name for category in row.categories.all()])

admin.site.register(models.Question, QuestionAdmin)

class SolveLogAdmin(admin.ModelAdmin):
    inlines = [UserInline, FlagInline]

admin.site.register(models.SolveLog)

class TrackingAdmin(admin.ModelAdmin):
    inlines = [UserInline]
