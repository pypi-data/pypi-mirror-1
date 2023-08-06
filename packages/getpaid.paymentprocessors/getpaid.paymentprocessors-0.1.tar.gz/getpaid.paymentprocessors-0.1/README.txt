Purpose
-------

This package provides generic payment processor registration methods. Though the code itself is free from Plone dependencies,
this documentation covers Plone too.

Preface
-------

GetPaid provides support for two different kind of payment processors:

- *Synchronous*: Your web server does the payment authorization by doing a remote procedure call to the payment processor server
  You need to override payment processor checkout-review-pay wizard step to have your own custom form fields
  needed for the payment submission. The default Products.PloneGetPaid.browser.checkout.CheckoutReviewAndPay
  provides fields for simple credit card payment.

- *Asynchronous*: The buyer will leave your site for the payment to the payment web server (PayPal) and come back to your site after
  the payment is completed

Installation
------------

Install GetPaid from trunk. 

Use branch following development branches. Note that PayPal changes are in trunk::

	cd src
	rm -rf Products.PloneGetPaid
	rm -rf getpaid.nullpayment
	rm -rf getpaid.paypal
	svn co https://getpaid.googlecode.com/svn/Products.PloneGetPaid/branches/multiplepaymentprocessors Products.PloneGetPaid
	svn co https://getpaid.googlecode.com/svn/getpaid.nullpayment/branches/multiplepaymentprocessors getpaid.nullpayment
	svn co https://getpaid.googlecode.com/svn/getpaid.paypal/trunk getpaid.paypal
	
Add *getpaid.paymentprocessers* to your *316.cfg* eggs and develop-eggs sections.

Administration
--------------

Active payment processors must be enabled in *Site setup* -> *GetPaid* -> *Payment processor settings*.

You can manage individual payment processor settings from the same screen.

Checkout wizard steps
---------------------

A checkout wizard contains a step "checkout-payment-method" which allows the user to select 
the wanted payment method. This step is only available if the site has more than 
one active payment processors.

Creating your own payment processor
-----------------------------------

Payment processor directive
===========================

Payment processors are registered using a ZCML directive::

    <!-- Register logic class dealing with the actual payment -->

  	<adapter
     for="getpaid.core.interfaces.IStore"
     provides="getpaid.core.interfaces.IPaymentProcessor"
     factory=".null.NullPaymentAdapter"
     name="Testing Processor"
     />

    <!-- Register payment processor specific user interface parts -->

    <paymentprocessors:registerProcessor
       name="Testing Processor"
	   i18n_name="Test Payment"
       selection_view="null_payment_button"
       review_pay_view="null_payment_pay_page"
       thank_you_view="null_payment_thank_you_page"
       settings_view="null_payment_settings_page"
       />


It is recommended best practice to put paymentprocessor directive into a separate ZCML file in your getpaid extension module
to maintain backwards compatibility. You can do it using zcml condition::

  <include zcml:condition="installed getpaid.paymentprocessors" file="paymentprocessors.zcml" />
  
You can also maintain backward compatiblity overrides with not-installed directive::

  <include zcml:condition="not-installed getpaid.paymentprocessors" package=".browser" file="overrides.zcml" />


paymentprocessors:registerProcessor attributes
++++++++++++++++++++++++++++++++++++++++++++++

Below is explanation for **registerProcessor** attributes.

**name**: This must match getpaid.core.interfaces.IPaymentProcessor adapter name

**i18_name**: This is the user visible name of the payment processor. It might appear in the summaries and listing.
  Term "payment method" is recommended here for more end user friendly language.

**selection_view**: This is a <browser:page> registration name which renders the payment method selection button on payment
method selection checkout wizard step. The browser view class should be subclasses from Products.GetPaid.browser.checkout.BasePaymentMethodButton.

selection_view template should render a <tr> element which is rendered on the checkout payment method selection page. It contains three columns:

	- <td> having <input type="radio"> button with accessibility <label>

	- <td> with payment method name/logo image

	- <td> with description. You can override this template to have clauses like "Using PayPal will cost 2$ extra"

For example, see getpaid.nullpayment/templates/button.pt

**review_pay_view**: This view renders payment processor specific "review and pay" view in the checkout wizard. The attribute
holds the registered <browser:page> name. This view should be subclass of Products.PloneGetPaid.browser.checkout.CheckoutReviewAndPay.
To change the review and pay page template, override template attribute of the class.

Usually review and pay page has two purposes::

	- Render a <form> which is submitted to the payment authorization server with a callback back to the shop server

	- Do a HTTP redirect or Javascript redirect and take the user to the payment authorization server for an external review payment page

Because review_pay_view is based of BaseCheckoutForm class, you need to explitcly subclass it and override
*template* class attribute to use your own template. Using <browser:page template="..."> does not work.

**settings_view**: This view renders the settings for the payment processor. It should
be subclass of Products.PloneGetPaid.admin.PaymentProcessor.

**thank_you_view**: This should point to the <browser:page> which is rendered after the payment processor is complete. It is unused currently.
Payment processor review_pay_view is itself responsible to point the user back to the shop site after the payment has been authorized.

See https://getpaid.googlecode.com/svn/getpaid.nullpayment/branches/multiplepaymentprocessors/src/getpaid/nullpayment/paymentprocessors.zcml
for more info.

Testing
-------

Units tests can be found in *Products.PloneGetPaid.tests.test_payment_processors*. 

It is recommended to take a look these how to programmatically play around with the checkout wizard and
test your custom payment methods automatically.

Non-plone related functionality is tested in getpaid.paymentprocessors.tests. 
This mainly involves testing ZCML validy.

Guidelines for payment processor plug-in authors
------------------------------------------------

- See getpaid.paypal how to include all related browser/ module extensions, including necessary media files

- In your payment processor README include short, but detailed, instructions

	- For testing the payment processor in sandbox mode

	- For settings up the payment processor in production mode

- In your payment processor README include link to payment processor logo usage terms

Developer snippets
-------------------

Payment processors are described by Entry objects which simply hold the information provided by IRegisterPaymentProcessorDirective.

To get site wide active payment processors call::

	from Products.PloneGetPaid import payment

	processors = payment.getActivePaymentProcessors(context) # context = any Plone site object

In checkout wizard, you can get the user chosen payment method using the following snippet. You can do this *after* the user
has passed payment method selection step::

	payment_processor_name = wizard.getActivePaymentProcessor()

To get the actual payment processor instance by its name call::

	from zope.component import getUtility, getAdapter
	from Products.CMFCore.utils import getToolByName
	import getpaid.core.interfaces

    site_root = getToolByName(self.context, "portal_url").getPortalObject()
	processor = component.getAdapter(site_root, getpaid.core.interfaces.IPaymentProcessor, payment_processor_name)

Payment processor registry is available in getpaid.paymentprocessors.registry.paymentProcessorRegistry. This registry
holds the data of registered payment processor code objects.

Activated payment processor names are stored in portal_properties as LinesField::

	# sequence of unicode strings, payment processor names
	portal_properties.payment_processor_properties.enabled_processors

Accessing payment information in the stored order::

	info = order.payment_method # IPaymentMethodInformation instance
	info.payment_processor == u"Your Processor Name"

TODO
----

- Rip off interfaces.IGetPaidManagementOptions(self.context).processor_name from everywhere

- Remove "Set active processor" setting and Payment options page in site setup

- Discuss whether it is sensible to use portal_properties to store settings (AFAIK this is the best
  practice since they can be edited plain text is site setup breaks down)

- Handle validation if user chooses no payment processor

- Remember checked payment processor in the checkout wizard

- There is a bug that wizard.data_manager.payment_method.payment_processor pulls out i18n_name for some reason.
  Unless fixed payment processor name must be i18n_name.

- How/when asyncronous processors should create Order, toggle workflow states and delete cart?

