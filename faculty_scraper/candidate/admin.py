from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from candidate.models import *


class CandidateRecommenderInline(admin.TabularInline):
    model = CandidateRecommender 
    fields = ['prefix', 'fullname', 'title', 'institution', 'email', 'relation']
    extra=0

class CandidateDegreeInline(admin.TabularInline):
    model = CandidateDegree
    fields = ['degree_type', 'institution', 'degree_date', 'field_of_study']
    extra=0

class RecommenderDocumentInline(admin.TabularInline):
    model = RecommenderDocument
    fields = ['recommender_id', 'doc_name', 'doc_fullpath', 'is_uploaded']
    extra=0

class CandidateDocumentInline(admin.TabularInline):
    model = CandidateDocument
    fields = ['doc_type', 'doc_name', 'is_uploaded']
    extra=0


class CandidateAdmin(admin.ModelAdmin):
    inlines = (CandidateDegreeInline,CandidateRecommenderInline, RecommenderDocumentInline, CandidateDocumentInline)
    save_on_top = True
    readonly_fields= ['recommendation_cnt', 'aries_link']
    
    search_fields = ('aries_id', 'lname', 'fname', 'email',  )
    list_display = ( 'lname', 'fname', 'aries_id','email', 'title','recommendation_cnt', 'last_update', 'aries_link')
    
    fieldsets = [
           ('Name',               {'fields': [ 'prefix', 'fname', 'mi', 'lname',  'suffix'  ]}),
           ('Aries Info', {'fields': [ ('aries_id', 'aries_link',) ]}),#'aries_username'
           ('Title', {'fields': [ 'title', 'institution', ]}),
           ('Contact', {'fields': ['email', 'phone',]}),
           ('Address', {'fields': ['addr1', 'addr2', 'addr3', 'city', 'state', 'postal_code', 'country' ]}),
           
           #('Required Docs', {'fields': ['cv', 'cover_letter', 'teaching_philosophy','research', 'pub1']}),
           #('Optional Docs', {'fields': ['pub2', 'pub3', 'pub4','pub5']}),
       ]
    
admin.site.register(Candidate, CandidateAdmin)


class CandidateDegreeAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('candidate__lname', 'candidate__fname', 'candidate__aries_id','degree_type', 'institution', 'degree_date', 'field_of_study',)
    list_display = ('candidate', 'degree_type', 'institution', 'degree_date', 'field_of_study',)
    list_filter = ['degree_type',]
admin.site.register(CandidateDegree, CandidateDegreeAdmin)



class CandidateDocumentAdmin(admin.ModelAdmin):
    save_on_top = True
    readonly_fields= ['last_update']
    
    search_fields = ('candidate__lname', 'candidate__fname', 'candidate__aries_id', )
    list_display = ('candidate', 'doc_name', 'doc_type', 'is_uploaded', 'last_update',)
    list_filter = ['is_uploaded', 'doc_type']
admin.site.register(CandidateDocument, CandidateDocumentAdmin)


class RefereeFormAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('candidate__lname', 'candidate__fname', 'candidate__aries_id', )
    list_display = ('candidate', 'recommender_id', 'fullname', 'institution', 'email',)
admin.site.register(RefereeForm, RefereeFormAdmin)

class CandidateRecommenderAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('candidate__lname', 'candidate__fname', 'candidate__aries_id', 'prefix', 'fullname', 'title', 'institution',  'email', )
    list_display = ('candidate', 'prefix', 'fullname', 'title', 'institution',  'email',)
admin.site.register(CandidateRecommender, CandidateRecommenderAdmin)

class RecommenderDocumentAdmin(admin.ModelAdmin):
    save_on_top = True
    readonly_fields= ['last_update']
    
    search_fields = ('candidate__lname', 'candidate__fname', 'candidate__aries_id', 'doc_name',)
    list_display = ('candidate', 'doc_name',  'is_uploaded', 'last_update',)
    list_filter = ['is_uploaded']
admin.site.register(RecommenderDocument, RecommenderDocumentAdmin)

class DocumentTypeAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('name', 'id')

admin.site.register(DocumentType, DocumentTypeAdmin)

