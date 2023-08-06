from operator import itemgetter

from plone.i18n.locales.interfaces import IContentLanguageAvailability
from zope.component import adapts
from zope.component import getAllUtilitiesRegisteredFor
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.locales import locales, LoadLocaleError
from zope.interface import Interface
from zope.publisher.interfaces import IRequest
from zope.publisher.browser import BrowserView

from AccessControl import getSecurityManager
from AccessControl.Permissions import view as View
from OFS.interfaces import IApplication
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.GenericSetup import profile_registry
from Products.GenericSetup import BASE, EXTENSION
from ZPublisher.BaseRequest import DefaultPublishTraverse

from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.factory import addPloneSite
from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFPlone.interfaces import IPloneSiteRoot


class AppTraverser(DefaultPublishTraverse):
    adapts(IApplication, IRequest)

    def publishTraverse(self, request, name):
        if name == 'index_html':
            view = queryMultiAdapter((self.context, request),
                        Interface, 'plone-overview')
            if view is not None:
                return view
        return DefaultPublishTraverse.publishTraverse(self, request, name)


class Overview(BrowserView):

    def sites(self, root=None):
        if root is None:
            root = self.context
        
        result = []
        secman = getSecurityManager()
        for obj in root.values():
            if IPloneSiteRoot.providedBy(obj):
                if secman.checkPermission(View, obj):
                    result.append(obj)
            elif obj.getId() in getattr(root, '_mount_points', {}):
                result.extend(self.sites(root=obj))
        return result

    def outdated(self, obj):
        mig = obj.get('portal_migration', None)
        if mig is not None:
            return mig.needUpgrading()
        return False


class FrontPage(BrowserView):

    index = ViewPageTemplateFile('templates/plone-frontpage.pt')


class AddPloneSite(BrowserView):

    def profiles(self):
        base_profiles = []
        extension_profiles = []
        default_extension_profiles = [
            'plonetheme.sunburst:default',
            'plonetheme.classic:default',
            ]

        # profiles available for install/uninstall, but hidden at the time
        # the Plone site is created
        not_installable = [
            'plonetheme.classic:uninstall',
        ]
        utils = getAllUtilitiesRegisteredFor(INonInstallable)
        for util in utils:
            not_installable.extend(util.getNonInstallableProfiles())

        for info in profile_registry.listProfileInfo():
            if info.get('type') == EXTENSION and \
               info.get('for') in (IPloneSiteRoot, None):
                profile_id = info.get('id')
                if profile_id not in not_installable:
                    if profile_id in default_extension_profiles:
                        info['selected'] = 'selected'
                    extension_profiles.append(info)
        extension_profiles.sort(key=itemgetter('title'))

        for info in profile_registry.listProfileInfo():
            if info.get('type') == BASE and \
               info.get('for') in (IPloneSiteRoot, None):
                base_profiles.append(info)

        return dict(
            base = tuple(base_profiles),
            default = _DEFAULT_PROFILE,
            extensions = tuple(extension_profiles),
        )

    def browser_language(self):
        language = 'en'
        pl = IUserPreferredLanguages(self.request)
        if pl is not None:
            languages = pl.getPreferredLanguages()
            for httplang in languages:
                parts = (httplang.split('-') + [None, None])[:3]
                if parts[0] == parts[1]:
                    # Avoid creating a country code for simple languages codes
                    parts = [parts[0], None, None]
                elif parts[0] == 'en':
                    # Avoid en-us as a language
                    parts = ['en', None, None]
                try:
                    locale = locales.getLocale(*parts)
                    language = locale.getLocaleID().replace('_', '-').lower()
                    break
                except LoadLocaleError:
                    # Just try the next combination
                    pass
        return language

    def languages(self, default='en'):
        util = queryUtility(IContentLanguageAvailability)
        if '-' in default:
            available = util.getLanguages(combined=True)
        else:
            available = util.getLanguages()
        languages = [(code, v.get(u'native', v.get(u'name'))) for
                     code,v in available.items()]
        languages.sort(key=itemgetter(1))
        return languages

    def __call__(self):
        context = self.context
        form = self.request.form
        submitted = form.get('form.submitted', False)
        if submitted:
            site_id = form.get('site_id', 'Plone')
            site = addPloneSite(
                context, site_id,
                title=form.get('title', ''),
                profile_id=form.get('profile_id', _DEFAULT_PROFILE),
                extension_ids=form.get('extension_ids', ()),
                setup_content=form.get('setup_content', False),
                default_language=form.get('default_language', 'en'),
                )
            self.request.response.redirect(site.absolute_url())

        return self.index()


class Upgrade(BrowserView):

    def upgrades(self):
        ps = getattr(self.context, 'portal_setup')
        return ps.listUpgrades(_DEFAULT_PROFILE)

    def versions(self):
        pm = getattr(self.context, 'portal_migration')
        result = {}
        result['instance'] = pm.getInstanceVersion()
        result['fs'] = pm.getFileSystemVersion()
        result['equal'] = result['instance'] == result['fs']
        result['corelist'] = pm.coreVersions()
        return result

    def __call__(self):
        context = self.context
        form = self.request.form
        submitted = form.get('form.submitted', False)
        if submitted:
            pm = getattr(self.context, 'portal_migration')
            report = pm.upgrade(
                REQUEST=self.request,
                dry_run=form.get('dry_run', False),
                )
            return self.index(report=report)

        return self.index()
