from Acquisition import aq_inner

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from collective.portlet.contentsearch import ContentSearchPortletMessageFactory as _

from zope.component import getMultiAdapter

class ContentSearchView(BrowserView):
    template = ViewPageTemplateFile('templates/content_search.pt')

    def __call__(self):
        context = aq_inner(self.context)

#        form = self.request.form
#        add_many_to_cart_button = form.get('form.button.AddManyToCart', None) is not None
##        new_button = form.get('form.button.NewButton', None) is not None
#        go_to_cart_button = form.get('form.button.GoToCart', None) is not None

#        # Defines
#        context= aq_inner(self.context)
#        context_state = self.context.restrictedTraverse("@@plone_context_state")
#        url = context_state.view_url()
#        sdm = getToolByName(context, "session_data_manager")
#        catalog = getToolByName(context, 'portal_catalog')
#        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
#        portal_url = portal_state.portal_url()

#        if add_many_to_cart_button:
#            session = sdm.getSessionData(create=True)
#            uid_amount_dictionary = session.get('cart_contents')
#            new_uid_amount = form.get('quantity')
##            if uid_amount_dictionary == (None or {}):
#            if uid_amount_dictionary == None or uid_amount_dictionary == {}:
#                session.set('cart_contents', new_uid_amount) 
#                return self.template()
#            else:
#                #Because session.get('cart_contents') give you instance, convert it to dictionary.
#                uid_amount_dictionary = dict(session.get('cart_contents'))
#                item = catalog(UID=new_uid_amount.keys()[0])
#                i = item[0].getObject()
#                if uid_amount_dictionary.has_key(new_uid_amount.keys()[0]):
#                    new_amount = int(uid_amount_dictionary[new_uid_amount.keys()[0]]) + int(new_uid_amount.values()[0])
#                    if new_amount > i.stock:
#                        new_amount = i.stock
#                        new_uid_amount = {i.UID(): new_amount}
#                        uid_amount_dictionary.update(new_uid_amount)
#                        session.set('cart_contents', uid_amount_dictionary)
#                        return self.template()
#                    else:
#                        new_uid_amount = {i.UID(): new_amount}
#                        uid_amount_dictionary.update(new_uid_amount)
#                        session.set('cart_contents', uid_amount_dictionary)
#                        return self.template()
#                else:
#                        uid_amount_dictionary.update(new_uid_amount)
#                        session.set('cart_contents', uid_amount_dictionary)
#                        return self.template()
#        if go_to_cart_button:
#            return self.request.response.redirect('%s/@@cart-view' % portal_url)
#        else:
#            return self.template()

        return self.template()

#    def selected_currency(self):
#        context = aq_inner(self.context)
#        membership = getToolByName(context, 'portal_membership')
#        sc = membership.getAuthenticatedMember().getProperty('currency')
#        if sc == u"eur":
#            return None
#        else:
#            for curren in available_currencies:
#                if curren[0] == sc:
#                    return _(curren[1])
#                    break

#    def selected_currency_code(self):
#        context = aq_inner(self.context)
#        currency_provider = ICurrencyProvider(context)
#        return currency_provider.selected_currency_code


#    def price_with_selected_currency_code(self):
#        """Returns price with selected currency in string."""
##        context= aq_inner(self.context)
###        malltool = getToolByName(context, 'portal_malltool')
###        membership = getToolByName(context, 'portal_membership')
###        sc = membership.getAuthenticatedMember().getProperty('currency')
###        if sc == "eur":
###            return None
###        else:
###            calculated_currency = malltool.getCalculatedCurrencyRate()
###            price = context.getPrice()
###            for curren in available_currencies:
###                if curren[0] == sc:
###                    if curren[2] == 0:
###                        return '%.2f' %(float(price) * calculated_currency)
###                    else:
###                        return '%.f' %(float(price) * calculated_currency)
##        return context.price_with_selected_currency()
#        context = aq_inner(self.context)
#        currency_provider = ICurrencyProvider(context)
#        return currency_provider.price_with_selected_currency_code(float(context.price))

#    def selected_country(self):
#        context = self.context
#        membership = getToolByName(context, 'portal_membership')
#        sc = membership.getAuthenticatedMember().getProperty('country')
#        if sc == "jp":
#            return True
#        else:
#            return False

#    def tax_free_price(self):
#        """Tax free price in string"""
#        context= aq_inner(self.context)
#        return '%.2f' %(context.tax_free_price())

#    def tax_free_price_with_selected_currency(self):
#        """Returns tax free price with selected currency in string"""
#        context= aq_inner(self.context)
##        malltool = getToolByName(context, 'portal_malltool')
##        membership = getToolByName(context, 'portal_membership')
##        sc = membership.getAuthenticatedMember().getProperty('currency')
##        if sc == "eur":
##            return None
##        else:
##            calculated_currency = malltool.getCalculatedCurrencyRate()
##            price = context.getPrice()
##            vat = context.getVat()
##            for curren in available_currencies:
##                if curren[0] == sc:
##                    if curren[2] == 0:
##                        return '%.f' %(float(price) * calculated_currency * 100 / (100 + float(vat)))
##                    else:
##                        return '%.2f'%(float(price) * calculated_currency * 100 / (100 + float(vat)))
#        return context.tax_free_price_with_selected_currency()

#    def variants(self):
#        """Returns list of variants containing its value."""
#        context = aq_inner(self.context)
##        catalog = getToolByName(context, 'portal_catalog')
##        malltool = getToolByName(context, 'portal_malltool')
##        context_path = '/'.join(context.getPhysicalPath())
##        variants = []
##        variants_catalog = catalog(
##            path=dict(query=context_path, depth=1),
##            object_provides=IShopItem.__identifier__,
##            review_state='published',
##            )
##        if list(variants_catalog) == []:
##            return False
##        else:
##            for variant in variants_catalog:
##                variant_path = variant.getPath()
##                obj = variant.getObject()
##                sub_variants = catalog(
##                    path=dict(query=variant_path, depth=1),
##                    object_provides=IShopItem.__identifier__,
##                    review_state='published',
##                        )
##                subs = []
##                for sub_variant in sub_variants:
##                    sub_obj = sub_variant.getObject()
##                    if (float(sub_obj.price) > 0 and 
##                        sub_obj.weight > 0):
##                            subs.append(sub_obj)
##                if (list(subs) == [] and 
##                    obj.weight > 0 and 
##                    float(obj.price) > 0):
##                    variants.append(dict(
##                                title=variant.Title,
##                                uid=variant.UID,
##                                sku=obj.sku,
##                                price=obj.price,
##                                selected_price=int(float(obj.price) * self.calculated_price()),
##                                stock=obj.stock,
##                                stock_list = self.stock_list_for_variants(obj.stock),
##                                obj=variant.getObject(),
##                                url=variant.getURL(),
##                           ))
##                else:
##                    False
##            return variants
#        return context.variants()

#    def stock_list(self):
#        """Number of stocks for selection."""
#        if self.necessary_field_has_value():
#            context= aq_inner(self.context)
#            stock = context.stock
#            stock_list_from_zero = range(stock)
#            stock_list_from_one = []
#            for l in stock_list_from_zero:
#                l = l + 1
#                stock_list_from_one.append(l)
#            return stock_list_from_one
#        else:
#            return False

#    def necessary_field_has_value(self):
#        context= aq_inner(self.context)
##        if context.weight > 0 and float(context.price) > 0 and context.stock > 0 and context.vat != None and context.weight_unit != None:
##            return True
##        else:
##            return False
#        return context.necessary_field_has_value()

#    def calculated_price(self):
#        context = aq_inner(self.context)
##        mtool = getToolByName(context, 'portal_malltool')
##        return mtool.currency_rate * (100 + mtool.currency_exchange_rate) / 100
#        return context.calculated_price()

#    def stock_list_for_variants(self, stock):
#        l = []
#        if stock >0:
#            for st in range(stock):
#                l.append(st+1)
#        return l

#    def sold_out(self):
#        context= aq_inner(self.context)
##        if (context.weight > 0 and 
##            float(context.price) > 0 and 
##            context.vat != None and 
##            context.weight_unit != None and 
##            self.stock_list() == False):
##            return True
##        else:
##            return False
#        return context.sold_out()
