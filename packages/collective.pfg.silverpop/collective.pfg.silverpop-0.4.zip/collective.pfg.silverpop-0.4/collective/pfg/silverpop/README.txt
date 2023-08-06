Introduction
************

This test shows how a PFG Form folder is added. We 
also add our custom **FormSilverpopAdapter**, configure 
it and show how the actual sent XML looks.

Setup
-----

First, we must perform some setup. We use the testbrowser that is shipped
with Five, as this provides proper Zope 2 integration. Most of the 
documentation, though, is in the underlying zope.testbrower package.

    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()
    >>> portal_url = self.portal.absolute_url()

The following is useful when writing and debugging testbrowser tests. It lets
us see all error messages in the error_log.

    >>> self.portal.error_log._ignored_exceptions = ()

With that in place, we can go to the portal front page and log in. We will
do this using the default user from PloneTestCase:

    >>> from Products.PloneTestCase.setup import portal_owner, default_password

    >>> browser.open(portal_url)

We have the login portlet, so let's use that.

    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()

Here, we set the value of the fields on the login form and then simulate a
submit click.

We also set the roles we want to have::
    >>> self.setRoles(['Member', 'Manager'])

We monkeypatch urllib to prohibit making requests to silverpop and get test output 
(url, headers, data).


We use a little helper function to get pretty output::

    >>> import textwrap
    >>> def print_lines(text, maxwidth=70):
    ...     lines = textwrap.wrap(text,maxwidth)
    ...     for line in lines:
    ...         print line


We create a Fake class to be returned by urlib2.urlopen::

    >>> class Fake(object):
    ...     def read(self): return ""

In our test method, we print request's url, headers, data (we decode
the urlencoded data for the test) and
return a Fake object::

    >>> import cgi
    >>> def test_urlopen(req):
    ...     print_lines(str(req.get_full_url()))
    ...     print_lines(str(req.headers))
    ...     print_lines(dict(cgi.parse_qsl(req.data))['xml'])
    ...     return Fake()
    >>> import urllib2

Finally we patch urllib2.urlopen::

    >>> urllib2.urlopen = test_urlopen

We also define a FakeRequest class to define our request
containing just a form::

    >>> class FakeRequest(dict):
    ...   def __init__(self, **kwargs):
    ...     self.form = kwargs

Adding content
--------------

Add a new Form Folder::

    >>> browser.getLink('Form Folder').click()
    >>> browser.getControl('Title').value = 'testform'
    >>> browser.getControl('Save').click()

    >>> 'testform' in browser.contents
    True

Go to the new Form Folder:

    >>> browser.getLink('testform').click()


We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'FormSilverpopAdapter' and click the 'Add' button to get to the add form.

    >>> browser.getControl('FormSilverpopAdapter').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'FormSilverpopAdapter' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'testadapter'
    >>> browser.getControl('Silverpop API URL').value = 'http://url.com'
    >>> browser.getControl('Silverpop List Id').value = '1'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

We added a new 'FormSilverpopAdapter' content item to the testform.

onSuccess
---------

On submit of the form, the onSuccess method of
our FormSilverpopAdapter will be called.

For this test, we are going to create some fields manually, so we need the classes::

    >>> from Products.PloneFormGen.content.fields import FGStringField, FGBooleanField

We also want to access our testadapter directly::

    >>> self.testadapter = self.portal.testform.testadapter

Field Name Policy
+++++++++++++++++

We enforce the following policies regarding the field names which we send to
SilverPop via their API:

- field names MUST start with a common perfix: "silverpop\_"
- there must be one field "silverpop_email"

We have a transformation function which does that::

    >>> from collective.pfg.silverpop.utilities import transform_column_name
    >>> transform_column_name("silverpop_foo")
    'foo'
    >>> transform_column_name("no_prefix") is None
    True

There's one special column name which is enforced to comply with the API from
SilverPop -- `email` is transformed to `EMAIL`::

    >>> transform_column_name("silverpop_email")
    'EMAIL'

CONFIRMATION
++++++++++++

Newsletter forms usually contain some confirmation field (yes I want to get the newsletter).
First we set up some fields to use later::

    >>> email = FGStringField('silverpop_email')
    >>> email.setId('silverpop_email')
    >>> confirm = FGBooleanField('silverpop_confirm')
    >>> confirm.setId('silverpop_confirm')

If the form doesn't contain a field with id **confirm**, 
we just make a request to silverpop.

We set up the fields, here we use only one field EMAIL::

    >>> fields = [email,]

We also set up a minimal request, containing the user's input::

    >>> request = FakeRequest(silverpop_email='x@x.com')

We now call the adapter's onSuccess method::

    >>> self.testadapter.onSuccess(fields,request)
    http://url.com
    {'Content-type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    <Envelope><Body><AddRecipient><LIST_ID>1</LIST_ID><CREATED_FROM>2</CRE
    ATED_FROM><UPDATE_IF_FOUND>true</UPDATE_IF_FOUND><COLUMN><NAME>EMAIL</
    NAME><VALUE>x@x.com</VALUE></COLUMN></AddRecipient></Body></Envelope>

USER DEFINED MAPPING
++++++++++++++++++++

We offer the ability, to define a mapping from
field ids to Silverpop API Keys::

    >>> self.testform = self.portal.testform

For this test we create some fields inside our form.

First, we create fields which should be regarded by our 'FormSilverpopAdapter'.

The special 'sivlerpop_email' field (this field has a fixed mapping)::

    >>> self.testform.invokeFactory('FormStringField', 'silverpop_email', title='Email')
    'silverpop_email'

A field to insert a name::

    >>> self.testform.invokeFactory('FormStringField', 'silverpop_name', title='Name')
    'silverpop_name'

We also create a misc field, which shouldn't be regarded, although 
it is in the same form::

    >>> self.testform.invokeFactory('FormStringField', 'credits_to_admin', title='Give your credits to the admin of the site')
    'credits_to_admin'


NO MAPPING
..........

First, we check what happens when we don't change the mapping.

We go to the 'FormSilverpopAdapter' s edit form::

    >>> browser.open(portal_url+'/testform/testadapter/edit')

The current mapping should only contain one record
(with columns id, title, silverpop api key),
so we check all columns.

id::

    >>> browser.getControl(name='mapping.id:records').value
    'silverpop_name'

title::

    >>> browser.getControl(name='mapping.title:records').value
    'Name'

silverpop api key::

    >>> browser.getControl(name='mapping.silverpop api key:records', index=0).value
    ''

We set up the list of fields::

    >>> fields = [self.testform.silverpop_email, self.testform.silverpop_name, self.testform.credits_to_admin,]

We set up a minimal request, containing the user's input::

    >>> request = FakeRequest(silverpop_email='x@x.com', silverpop_name='Hans', credits_to_admin='I like the high availability')

We now call the adapter's onSuccess method::

    >>> self.testadapter.onSuccess(fields,request)
    http://url.com
    {'Content-type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    <Envelope><Body><AddRecipient><LIST_ID>1</LIST_ID><CREATED_FROM>2</CRE
    ATED_FROM><UPDATE_IF_FOUND>true</UPDATE_IF_FOUND><COLUMN><NAME>name</N
    AME><VALUE>Hans</VALUE></COLUMN><COLUMN><NAME>EMAIL</NAME><VALUE>x@x.c
    om</VALUE></COLUMN></AddRecipient></Body></Envelope>


CUSTOM MAPPING
..............

Now, we check what happens when we change
the mapping.
We want to use 'FIRST NAME' as COLUMN 
for silverpop, for the 'silverpop_name'
field.

We go to the 'FormSilverpopAdapter' s edit form::

    >>> browser.open(portal_url+'/testform/testadapter/edit')

We change the value inside the mapping::

    >>> browser.getControl(name='mapping.silverpop api key:records', index=0).value = 'FIRST NAME'
    >>> browser.getControl('Save').click()

The list of fields, is still the same.

We set up a minimal request, containing the user's input::

    >>> request = FakeRequest(silverpop_email='x@x.com', silverpop_name='Hans', credits_to_admin='I like the high availability')

We now call the adapter's onSuccess method::

    >>> self.testadapter.onSuccess(fields,request)
    http://url.com
    {'Content-type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    <Envelope><Body><AddRecipient><LIST_ID>1</LIST_ID><CREATED_FROM>2</CRE
    ATED_FROM><UPDATE_IF_FOUND>true</UPDATE_IF_FOUND><COLUMN><NAME>FIRST N
    AME</NAME><VALUE>Hans</VALUE></COLUMN><COLUMN><NAME>EMAIL</NAME><VALUE
    >x@x.com</VALUE></COLUMN></AddRecipient></Body></Envelope>
