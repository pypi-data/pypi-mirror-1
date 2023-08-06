# -*- coding: utf-8 -*-
"""Page Admin module."""
from pages import settings
from pages.models import Page, Content, PageAlias
from pages.http import get_language_from_request, get_template_from_request
from pages.utils import get_placeholders
from pages.utils import get_language_from_request
from pages.templatetags.pages_tags import PlaceholderNode
from pages.admin.utils import get_connected, make_inline_admin
from pages.admin.forms import PageForm
from pages.admin.views import traduction, get_content, sub_menu, list_pages_ajax
from pages.admin.views import change_status, modify_content, delete_content
from pages.permissions import PagePermission
from pages.http import auto_render
import pages.widgets

from django.contrib import admin
from django.utils.translation import ugettext as _, ugettext_lazy
from django.utils.encoding import force_unicode
from django.conf import settings as global_settings
from django.http import HttpResponseRedirect
from django.contrib.admin.util import unquote
from django.contrib.admin.sites import AlreadyRegistered
if global_settings.USE_I18N:
    from django.views.i18n import javascript_catalog
else:
    from django.views.i18n import null_javascript_catalog as javascript_catalog

from os.path import join


class PageAdmin(admin.ModelAdmin):
    """Page Admin class."""

    form = PageForm
    exclude = ['author', 'parent']
    # these mandatory fields are not versioned
    mandatory_placeholders = ('title', 'slug')
    general_fields = ['title', 'slug', 'status', 'target',
        'position', 'freeze_date']

    if settings.PAGE_USE_SITE_ID:
        general_fields.append('sites')
    insert_point = general_fields.index('status') + 1
    
    # Strange django behavior. If not provided, django will try to find
    # 'page' foreign key in all registered models
    inlines = []

    if settings.PAGE_TAGGING:
        general_fields.insert(insert_point, 'tags')

    # Add support for future dating and expiration based on settings.
    if settings.PAGE_SHOW_END_DATE:
        general_fields.insert(insert_point, 'publication_end_date')
    if settings.PAGE_SHOW_START_DATE:
        general_fields.insert(insert_point, 'publication_date')

    from pages.urlconf_registry import registry
    if(len(registry)):
        general_fields.append('delegate_to')
        insert_point = general_fields.index('status') + 1

    normal_fields = ['language']
    page_templates = settings.get_page_templates()
    if len(page_templates) > 0:
        normal_fields.append('template')
    normal_fields.append('redirect_to')
    normal_fields.append('redirect_to_url')
    fieldsets = (
        [_('General'), {
            'fields': general_fields,
            'classes': ('module-general',),
        }],
        (_('Options'), {
            'fields': normal_fields,
            'classes': ('module-options',),
        }),
    )

    class Media:
        css = {
            'all': [join(settings.PAGES_MEDIA_URL, path) for path in (
                'css/rte.css',
                'css/pages.css'
            )]
        }
        js = [join(settings.PAGES_MEDIA_URL, path) for path in (
            'javascript/jquery.js',
            'javascript/jquery.rte.js',
            'javascript/jquery.query.js',
            'javascript/pages.js',
            'javascript/pages_form.js',
        )]

    def urls(self):
        from django.conf.urls.defaults import patterns, url, include

        # Admin-site-wide views.
        urlpatterns = patterns('',
            url(r'^$', self.list_pages, name='page-index'),
            url(r'^(?P<page_id>[0-9]+)/traduction/(?P<language_id>[-\w]+)/$',
                traduction, name='page-traduction'),
            url(r'^(?P<page_id>[0-9]+)/get-content/(?P<content_id>[-\w]+)/$',
                get_content, name='page-traduction'),
            url(r'^(?P<page_id>[0-9]+)/modify-content/(?P<content_id>[-\w]+)/(?P<language_id>[-\w]+)/$',
                modify_content, name='page-traduction'),
            url(r'^(?P<page_id>[0-9]+)/delete-content/(?P<language_id>[-\w]+)/$',
                delete_content, name='page-delete_content'),
            url(r'^(?P<page_id>[0-9]+)/sub-menu/$',
                sub_menu, name='page-sub-menu'),
            url(r'^(?P<page_id>[0-9]+)/move-page/$',
                self.move_page, name='page-traduction'),
            url(r'^(?P<page_id>[0-9]+)/change-status/$',
                change_status, name='page-change-status'),
        )
        urlpatterns += super(PageAdmin, self).urls
        
        return urlpatterns

    urls = property(urls)

    def i18n_javascript(self, request):
        """Displays the i18n JavaScript that the Django admin
        requires.

        This takes into account the ``USE_I18N`` setting. If it's set to False, the
        generated JavaScript will be leaner and faster.
        """
        return javascript_catalog(request, packages='pages')

    def save_model(self, request, page, form, change):
        """Move the page in the tree if necessary and save every
        placeholder :class:`Content <pages.models.Content>`.
        """
        language = form.cleaned_data['language']
        target = form.data.get('target', None)
        position = form.data.get('position', None)
        page.save()

        # if True, we need to move the page
        if target and position:
            try:
                target = self.model.objects.get(pk=target)
            except self.model.DoesNotExist:
                pass
            else:
                target.invalidate()
                page.move_to(target, position)

        for name in self.mandatory_placeholders:
            data = form.cleaned_data[name]
            placeholder = PlaceholderNode(name)
            placeholder.save(page, language, data, change)

        for placeholder in get_placeholders(page.get_template()):
            if(placeholder.name in form.cleaned_data and placeholder.name
                    not in self.mandatory_placeholders):
                data = form.cleaned_data[placeholder.name]
                placeholder.save(page, language, data, change)
        
        page.invalidate()

    def get_fieldsets(self, request, obj=None):
        """
        Add fieldsets of placeholders to the list of already
        existing fieldsets.
        """
        general_fields = list(self.general_fields)
        perms = PagePermission(request.user)

        # some ugly business to remove freeze_date
        # from the field list
        general_module = {
            'fields': list(self.general_fields),
            'classes': ('module-general',),
        }
        
        default_fieldsets = list(self.fieldsets)
        if not perms.check('freeze'):
            general_module['fields'].remove('freeze_date')

        default_fieldsets[0][1] = general_module

        placeholder_fieldsets = []
        template = get_template_from_request(request, obj)
        for placeholder in get_placeholders(template):
            if placeholder.name not in self.mandatory_placeholders:
                placeholder_fieldsets.append(placeholder.name)

        additional_fieldsets = []
        additional_fieldsets.append((_('Content'), {
            'fields': placeholder_fieldsets,
            'classes': ('module-content',),
        }))

        return default_fieldsets + additional_fieldsets

    def save_form(self, request, form, change):
        """Given a ModelForm return an unsaved instance. ``change`` is True if
        the object is being changed, and False if it's being added."""
        instance = super(PageAdmin, self).save_form(request, form, change)
        instance.template = form.cleaned_data['template']
        if not change:
            instance.author = request.user
        return instance

    def get_form(self, request, obj=None, **kwargs):
        """Get a :class:`Page <pages.admin.forms.PageForm>` for the
        :class:`Page <pages.models.Page>` and modify its fields depending on
        the request."""
        form = super(PageAdmin, self).get_form(request, obj, **kwargs)

        language = get_language_from_request(request)
        form.base_fields['language'].initial = language
        if obj:
            initial_slug = obj.slug(language=language, fallback=False)
            initial_title = obj.title(language=language, fallback=False)
            form.base_fields['slug'].initial = initial_slug
            form.base_fields['title'].initial = initial_title
            form.base_fields['slug'].label = _('Slug')

        template = get_template_from_request(request, obj)
        page_templates = settings.get_page_templates()
        if len(page_templates) > 0:
            template_choices = list(page_templates)
            template_choices.insert(0, (settings.DEFAULT_PAGE_TEMPLATE,
                    _('Default template')))
            form.base_fields['template'].choices = template_choices
            form.base_fields['template'].initial = force_unicode(template)

        for placeholder in get_placeholders(template):
            name = placeholder.name
            if obj:
                initial = Content.objects.get_content(obj, language, name)
            else:
                initial = None
            form.base_fields[name] = placeholder.get_field(obj,
                language, initial=initial)

        return form

    def change_view(self, request, object_id, extra_context=None):
        """The ``change`` admin view for the
        :class:`Page <pages.models.Page>`."""
        language = get_language_from_request(request)
        extra_context = {
            'language': language,
            # don't see where it's used
            #'lang': current_lang,
            'page_languages': settings.PAGE_LANGUAGES,
        }
        try:
            obj = self.model.objects.get(pk=object_id)
        except self.model.DoesNotExist:
            # Don't raise Http404 just yet, because we haven't checked
            # permissions yet. We don't want an unauthenticated user to be able
            # to determine whether a given object exists.
            obj = None
        else:
            template = get_template_from_request(request, obj)
            extra_context['placeholders'] = get_placeholders(template)
            extra_context['traduction_languages'] = [l for l in
                settings.PAGE_LANGUAGES if Content.objects.get_content(obj,
                                    l[0], "title") and l[0] != language]
        extra_context['page'] = obj
        return super(PageAdmin, self).change_view(request, object_id,
                                                        extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        """The ``add`` admin view for the :class:`Page <pages.models.Page>`."""
        extra_context = {
            'language': get_language_from_request(request),
            'page_languages': settings.PAGE_LANGUAGES,
        }
        template = get_template_from_request(request)
        #extra_context['placeholders'] = get_placeholders(template)
        return super(PageAdmin, self).add_view(request, form_url,
                                                            extra_context)

    def has_add_permission(self, request):
        """Return ``True`` if the current user has permission to add a new
        page."""
        lang = get_language_from_request(request)
        return PagePermission(request.user).check('add', lang=lang)

    def has_change_permission(self, request, obj=None):
        """Return ``True`` if the current user has permission
        to change the page."""
        lang = get_language_from_request(request)
        return PagePermission(request.user).check('change', page=obj,
            lang=lang, method=request.method)

    def has_delete_permission(self, request, obj=None):
        """Return ``True`` if the current user has permission on the page."""
        lang = get_language_from_request(request)
        return PagePermission(request.user).check('change', page=obj,
            lang=lang)

    def list_pages(self, request, template_name=None, extra_context=None):
        """List root pages"""
        if not admin.site.has_permission(request):
            return admin.site.login(request)
        language = get_language_from_request(request)

        query = request.POST.get('q', '').strip()

        if query:
            page_ids = list(set([c.page.pk for c in
                Content.objects.filter(body__icontains=q)]))
            pages = Page.objects.filter(pk__in=page_ids)
        else:
            pages = Page.objects.root()

        context = {
            'language': language,
            'name': _("page"),
            'pages': pages,
            'opts': self.model._meta,
            'q': query
        }

        # sad hack for ajax
        # if template_name:
        #    self.change_list_template = template_name
        context.update(extra_context or {})
        change_list = self.changelist_view(request, context)
        #self.change_list_template = 'admin/pages/page/change_list.html'
        #
        return change_list

    def move_page(self, request, page_id, extra_context=None):
        """Move the page to the requested target, at the given
        position"""
        page = Page.objects.get(pk=page_id)

        target = request.POST.get('target', None)
        position = request.POST.get('position', None)
        if target is not None and position is not None:
            try:
                target = self.model.objects.get(pk=target)
            except self.model.DoesNotExist:
                pass
                # TODO: should use the django message system
                # to display this message
                # _('Page could not been moved.')
            else:
                page.invalidate()
                target.invalidate()
                page.move_to(target, position)
                return list_pages_ajax(request)
        return HttpResponseRedirect('../../')

for admin_class, model, options in get_connected():
    PageAdmin.inlines.append(make_inline_admin(admin_class, model, options))

try:
    admin.site.register(Page, PageAdmin)
except AlreadyRegistered:
    pass

class ContentAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'type', 'language', 'page')
    list_filter = ('page',)
    search_fields = ('body',)

#admin.site.register(Content, ContentAdmin)

class AliasAdmin(admin.ModelAdmin):
    list_display = ('page', 'url',)
    list_editable = ('url', )

try:
    admin.site.register(PageAlias, AliasAdmin)
except AlreadyRegistered:
    pass

