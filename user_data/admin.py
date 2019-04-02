from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.html import format_html
from admin_object_actions.admin import ModelAdminObjectActionsMixin
from .models import Profile, Student, Driver, Preferences, MissingUniversity, StudentProof


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'birthday', 'gender', 'phone')
    list_filter = ('user', 'birthday')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'university',
        'university_email',
        'university_id',
        'enroll_year',
        'course',
    )
    list_filter = ('university',)
    search_fields = ('user', 'university_id',)


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'car_make',
        'car_model',
        'car_color',
        'likes_pets',
        'likes_smoking',
        'likes_music',
        'likes_talking',
    )
    search_fields = ('user',)


@admin.register(Preferences)
class PreferencesAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'updates_notifications',
        'ratings_notifications',
        'news_notifications',
    )
    list_filter = (
        'updates_notifications',
        'ratings_notifications',
        'news_notifications',
    )
    search_fields = ('user',)


@admin.register(MissingUniversity)
class MissingUniversityAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'email',
        'university_name',
        'university_id',
        'university_email'
    )
    list_filter = ('university_name', 'name')
    search_fields = ('name', 'email', 'university_name', )


class StatusFilter(SimpleListFilter):
    title = 'Status'

    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            (None, 'Pendentes'),
            (StudentProof.approved_status, 'Aprovado'),
            (StudentProof.denied_status, 'Negado'),
            ('all', 'All'),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() in (StudentProof.approved_status, StudentProof.denied_status):
            return queryset.filter(status=self.value())
        elif self.value() is None:
            return queryset.filter(status=StudentProof.pending_status)
        return queryset


@admin.register(StudentProof)
class StudentProofAdmin(
        ModelAdminObjectActionsMixin,
        admin.ModelAdmin):

    def scan_url(self, obj):
        return format_html("<a target='_blank' href='{url}'>{url}</a>", url=obj.proof_scan_url)

    list_display = (
        'student',
        'created',
        'status'
    )

    fields = (
        'student',
        'contact_email',
        'status',
        'scan_url',
        'scan_results',
        'proof',
        'display_object_actions_detail',
    )

    readonly_fields = (
        'student',
        'proof',
        'status',
        'scan_url',
        'scan_results',
        'display_object_actions_detail',
    )

    list_filter = ('created', StatusFilter, 'student__university')
    search_fields = ('student__university_id', 'student__university_email', 'contact_email')

    object_actions = [
        {
            'slug': 'approve',
            'verbose_name': 'Aprovar',
            'verbose_name_past': 'Aprovado',
            'form_method': 'GET',
            'function': 'approve',
            'detail_only': True,
        },
        {
            'slug': 'deny',
            'verbose_name': 'Negar',
            'verbose_name_past': 'Negado',
            'form_method': 'GET',
            'function': 'deny',
            'detail_only': True,
        },
    ]

    def approve(self, obj, form):
        obj.approve()

    def deny(self, obj, form):
        obj.deny()
