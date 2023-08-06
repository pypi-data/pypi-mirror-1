from os.path import join
from datetime import datetime
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _, get_language
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.shortcuts import get_object_or_404
from publisher import MpttPublisher
from publisher.errors import PublisherCantPublish
from cms.utils.urlutils import urljoin
from cms import settings
from cms.models.managers import PageManager, PagePermissionsPermissionManager
from cms.models import signals as cms_signals
from cms.utils.page import get_available_slug
from cms.exceptions import NoHomeFound

from cms.models.pagemodel import Page


class ArticlePage(Page):
    body = models.TextField(_("body"))
