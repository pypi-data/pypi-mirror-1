
from django import forms

from django.utils.translation import ugettext as _, ugettext_lazy
from cms.admin.pageadmin import PageAdmin
from cms.admin.forms import PageForm
from article.models import *
from django.contrib import admin

class ArticlePageForm(PageForm):
    menu_title = forms.CharField(label=_("Menu Title"), widget=forms.TextInput(),
        help_text=_('Overwrite what is displayed in the menu'), required=False)
    body_text = forms.CharField(label=_("Article Body"), widget=forms.TextInput(),
        help_text=_('Article body text'), required=True)

class ArticlePageAdmin(PageAdmin):
    form = ArticlePageForm    

admin.site.register(ArticlePage, ArticlePageAdmin)

