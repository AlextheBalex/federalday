from django.contrib import admin
from basics.models import *

class DocumentAdmin(admin.ModelAdmin):
    list_display = ("legislative_period", "document_id", "date")

class PartyAdmin(admin.ModelAdmin):
    list_display = ("abbrev", "name")

class FunctionAdmin(admin.ModelAdmin):
    list_display = ("name",)

class RegularStatementAdmin(admin.ModelAdmin):
    list_display = ("speaker", "text_short_decorator", "document", "order_id", 'str_nouns_short_decorator', 'str_adjectives', 'str_persons')

class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name', "party", "function")


admin.site.register(Document, DocumentAdmin)
admin.site.register(Party, PartyAdmin)
admin.site.register(Function, FunctionAdmin)
admin.site.register(RegularStatement, RegularStatementAdmin)
admin.site.register(Speaker, SpeakerAdmin)



