=================
Pre import
=================
    >>> from Products.CMFCore.utils import getToolByName

Check Plone Root
---------------------
    >>> app.objectIds()
    ['Control_Panel', 'plone', 'acl_users', 'temp_folder', 'browser_id_manager', 'session_data_manager']
    >>> app.session_data_manager
    <SessionDataManager at /session_data_manager>

Setting up and logging in
-------------------------

We use zope.testbrowser to simulate browser interaction in order to show
the main flow of pages. This is not a true functional test, because we also
inspect and modify the internal state of the ZODB, but it is a useful way of
making sure we test the full end-to-end process of creating and modifying
content.

    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()
    >>> portal_url = self.portal.absolute_url()
    >>> portal_url
    'http://nohost/plone'

The following is useful when writing and debugging testbrowser tests. It lets
us see error messages properly.

    >>> browser.handleErrors = True
    >>> self.portal.error_log._ignored_exceptions = ()

We then turn off the various portlets, because they sometimes duplicate links
and text (e.g. the navtree, the recent recent items listing) that we wish to
test for in our own views. Having no portlets makes things easier.

    >>> from zope.component import getUtility, getMultiAdapter
    >>> from plone.portlets.interfaces import IPortletManager
    >>> from plone.portlets.interfaces import IPortletAssignmentMapping

    >>> left_column = getUtility(IPortletManager, name=u"plone.leftcolumn")
    >>> left_assignable = getMultiAdapter((self.portal, left_column), IPortletAssignmentMapping)
    >>> for name in left_assignable.keys():
    ...     del left_assignable[name]

    >>> right_column = getUtility(IPortletManager, name=u"plone.rightcolumn")
    >>> right_assignable = getMultiAdapter((self.portal, right_column), IPortletAssignmentMapping)
    >>> for name in right_assignable.keys():
    ...     del right_assignable[name]

Finally, we need to log in as the portal owner, i.e. an administrator user. We
do this from the login page.

    >>> browser.open(portal_url)
    >>> from Products.PloneTestCase.setup import portal_owner, default_password
    >>> browser.open(portal_url + '/login_form?came_from=' + portal_url)
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> try:
    ...     browser.getControl(name='submit').click()
    ... except:
    ...     print self.portal.error_log.getLogEntries()[0]['tb_text']
    ...     import pdb; pdb.set_trace()


    >>> browser.open(portal_url)

=============================================================================================
First install PloneGetPaid.
    >>> installer = getToolByName(portal, 'portal_quickinstaller')
    >>> installer.isProductAvailable('PloneGetPaid')
    True
    >>> self.portal.portal_quickinstaller.installProduct('PloneGetPaid')
    ''
    >>> len(installer.listInstalledProducts())
    1

    >>> try:
    ...     browser.open(portal_url)
    ... except:
    ...     print self.portal.error_log.getLogEntries()[0]['tb_text']
    ...     import pdb; pdb.set_trace()


Testing the setup aspects of GetPaid. Setting required settings.
    >>> browser.open(portal_url)
    >>> browser.getLink('Site Setup').click()
    >>> browser.getLink('GetPaid').click()
    >>> browser.getLink('Site Profile').click()
    >>> browser.getControl('Contact Email').value = 'info@plonegetpaid.com'
    >>> browser.getControl( name="form.store_name").value = 'Test this fake company'

Note: setting 'displayValue = ['UNITED STATES']' would give an
AmbiguityError as the browser does not understand that we do not mean
'UNITED STATES MINO' which is also an option.  So we set an
unambiguous value::

    >>> browser.getControl('Apply').click()
    >>> browser.getLink('GetPaid').click()
    >>> browser.getLink('Content Types').click()
    >>> browser.getLink('GetPaid').click()
    >>> browser.getLink('Payment Options').click()
    >>> browser.getControl(name = 'form.payment_processor').displayValue = ['Verkkomaksut payment interface']
    >>> browser.getControl(name = 'form.allow_anonymous_checkout.used').value = 'on'
    >>> browser.getControl('Apply').click()
    >>> browser.getLink('GetPaid').click()
    >>> browser.getLink('Payment Processor Settings').click()
    >>> fields_name = ['Merchant ID', 'Merchant Authentication Code']
    >>> for field in fields_name:
    ...     field in browser.contents 
    True
    True
    >>> browser.getControl('Merchant ID').value = '13466'
    >>> browser.getControl('Merchant Authentication Code').value = '6pKF4jkv97zmqBJ3ZL8gUw5DfT2NMQ'
    >>> browser.getControl('Apply').click()
    >>> browser.getLink('GetPaid').click()
    >>> browser.getLink('Email Notifications').click()
    >>> browser.getControl(name='form.merchant_email_notification').displayValue = ['Do not send merchant email notification of a completed transaction']
    >>> browser.getControl(name='form.customer_email_notification').displayValue = ['Do not send customer email notification of a completed transaction']
    >>> browser.getControl('Apply').click()
    >>> browser.getLink('GetPaid').click()
    >>> browser.getLink('Legal Disclaimers').click()
    >>> browser.getControl(name='form.disclaimer').value = 'Test disclaimer'
    >>> browser.getControl(name='form.privacy_policy').value = 'Test privacy policy'
    >>> browser.getControl('Apply').click()
    >>> browser.getLink('GetPaid').click() 
    >>> 'Test this fake company' in browser.contents
    True

Here we are setting the buyable types for use in the following tests
  
    >>> from Products.PloneGetPaid.interfaces import IGetPaidManagementOptions
    >>> options = IGetPaidManagementOptions(self.portal)
    >>> options.buyable_types = ['Link', 'Event']
    >>> options.donate_types = ['Document']
    >>> options.shippable_types = ['Document']

Here we set up the Credit cards accepted for payment:

   >>> options.accepted_credit_cards = ["Visa"]

Check to make sure the settings we put in Site Profile appear on this page. 

     >>> browser.getLink('Home').click()

Setup Donatable

    >>> browser.getLink('Make this a Donation').click()
    >>> browser.getControl(name='form.donation_text').value = 'Test donation description'
    >>> browser.getControl(name='form.price').value = '11.00'
    >>> browser.getControl('Activate').click()

Test donation checkout, which should go directly to checkout screen from the portlet. 
    >>> browser.getLink('Donate!').click()
    >>> saved_url = browser.url

Continue where we left of after clicking Donate.
    >>> browser.open(saved_url)
    >>> browser.getControl('Your Name').value = 'Test'
    >>> browser.getControl('Phone Number').value = '1234567'
    >>> browser.getControl('Phone Number').value = '12345678'
    >>> browser.getControl(name='form.email').value = 'test@test.com'
    >>> browser.getControl(name='form.bill_name').value = 'Test'
    >>> browser.getControl(name='form.bill_first_line').value = 'Test'
    >>> browser.getControl(name='form.bill_city').value = 'Test'
    >>> browser.getControl(name='form.bill_state').value = ('US-HI',)
    >>> browser.getControl(name='form.bill_postal_code').value = '12345'
    >>> browser.getControl(name='form.ship_first_line').value = 'Test'
    >>> browser.getControl(name='form.ship_city').value = 'Test'
    >>> browser.getControl(name='form.ship_state').value = ('US-HI',)
    >>> browser.getControl(name='form.ship_postal_code').value = '12345'

Now go to the next form.
    >>> try:
    ...     browser.getControl('Continue').click()
    ... except:
    ...     print self.portal.error_log.getLogEntries()[0]['tb_text']
    ...     import pdb; pdb.set_trace()
    >>> "Card Holder Name" in browser.contents
    False
