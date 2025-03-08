from django.contrib import admin

# Register your models here.


from .models import Signup, Contact
from .models import BlogPost
from .models import Service, Subscription


@admin.register(Signup)
class SignupAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'email', 'date_registered')
    search_fields = ('company_name', 'email')
    list_filter = ('date_registered',)
    
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'timestamp')
    search_fields = ('name', 'email', 'subject')
    
#register the BlogPost
admin.site.register(BlogPost)
  
#register the service and subscription models
admin.site.register(Service)
admin.site.register(Subscription)

