*************
About Formish
*************

Formish is a templating language agnostic form generation and handling library. 

Introduction - A Simple Form
============================

Creating a schema
-----------------

First of all we need to create a data schema to define what types of data we want in the form. Schema's use the 'Schemaish' package which lets you define structures against which you can validate/convert data. Lets take a look at the structure of a Form instance to begin with


>>> import schemaish
>>> schema = schemaish.Structure()
>>> schema.add( 'myfield', schemaish.String() )
>>> schema.attrs
[('myfield', <schemaish.attr.String object at 0x...>)]

Creating a form
---------------

So we now have a single field in our schema which is defined as a string. We can now create a form from this

>>> import formish
>>> form = formish.Form(schema)

Attributes of a form
^^^^^^^^^^^^^^^^^^^^

And what can we do with the form? Well at the moment we have a form name and some fields

>>> form.name
'formish'

>>> for field in form.fields:
...     print field
... 
<formish.forms.Field object at 0x...>

Attributes of a field
^^^^^^^^^^^^^^^^^^^^^

And what about our field? Well it's now become a form field, which means it has a few extra attributes to do with creating things like classes, ids, etc.

>>> field = form.fields.next()
>>> field.name
'myfield'

Obviously the name is what we have it.

>>> field.widget
<bound widget name="myfield", widget="Input", type="String">

>>> field.title
'Myfield'

The title, if not specified in the schema field, is derived from the form name by converting camel case into capitalised words.

>>> field.cssname
'formish-myfield'

This is the start of the templating stuff.. The cssname is an identifier that can be inserted into forms, used for ids and class names.

How to create HTML
------------------

We create our HTML by calling the form as follows..

>>> form()
'...<form id="formish" action="" class="formish-form" method="post" enctype="multipart/form-data" accept-charset="utf-8">...'

I've skipped the majority of this output as it's probably better shown formatted

.. code-block:: html

    <form id="formish" action="" class="formish-form" method="post" enctype="multipart/form-data" accept-charset="utf-8">
      <div>
        <input type="hidden" name="_charset_" />
        <input type="hidden" name="__formish_form__" value="formish" />
        <div id="formish-myfield-field" class="field string input">
          <label for="formish-myfield">Myfield</label>
          <div class="inputs">
            <input id="formish-myfield" type="text" name="myfield" value="" />
          </div>
        </div>
        <div class="actions">
          <input type="submit" id="formish-action-submit" name="submit" value="Submit" />
        </div>
      </div>
    </form>

What's in the HTML
------------------

Firstly we have the form setup itself. The form name/id can be set by passing it into the Form as follows.

>>> named_form = Form(schema,name='myformname')

Otherwise the form defaults to 'formish'. 

The method at the moment is always 'post' but a future release will implement get forms also. The final two attributes, enctype and accept-charset make the form behave in as consistent a way as possible. Defaulting to content type of 'utf-8' and handling the form data accoring to http://www.ietf.org/rfc/rfc2388.txt 'multipart/form-data'. 

The form html element
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: html

    <!-- The Form -->
    <form id="formish" action="" method="post" enctype="multipart/form-data" accept-charset="utf-8">

The first hidden field is '_charset_ which is a hack to help mozilla handle charsets as described here https://bugzilla.mozilla.org/show_bug.cgi?id=18643. The second is the name of the form, used after submission to work out which form has been returned.

The form configuration attributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


.. code-block:: html

      <!-- Form Configuration Attributes -->
      <input type="hidden" name="_charset_" />
      <input type="hidden" name="__formish_form__" value="formish" />


The field itself has an id, using the form name, field name and the suffix '-field' to help with javascript, css, etc. There are also a bunch of classes that allow global css to be applied to different widget types or schema types.

The label points at the field, which in this case is the only input field. In the case of a date parts widget (three input boxes), the label's for attribute would point at the first field.

The 'input's div is a container that holds the widget itself, in this case just a single input field with an id for the label to point at.

The input field(s)
^^^^^^^^^^^^^^^^^^

.. code-block:: html

      <!-- The String Field -->
      <div id="formish-myfield-field" class="field string input">
        <label for="formish-myfield">Myfield</label>
        <div class="inputs">
          <input id="formish-myfield" type="text" name="myfield" value="" />
        </div>
      </div>

The action(s)
^^^^^^^^^^^^^

Finally, the actions block contains all of the submit buttons - in this case just a single input with the default 'submit' value.

.. code-block:: html

      <!-- The Action(s) -->
      <div class="actions">
        <input type="submit" id="formish-action-submit" name="submit" value="Submit" />
      </div>
    </form>


Processing the Submitted Form
-----------------------------

Once the form is submitted, we can get the data by calling 'validate'. In order to simulate this, we're going to create a request object by hand using webob.. 

>>> import webob
>>> r = webob.Request.blank('http://localhost/', environ={'REQUEST_METHOD': 'POST'})
>>> r.POST['myfield'] = 'myvalue'
>>> form.validate(r)
{'myfield': u'myvalue'}

And that is our simple form overview complete. 

Introduction - A Slightly More Complex Form
===========================================

OK, We're going to put a more things together for this.. 

* A custom form name
* Different schema types
* different widgets
* Form errors

Creating the form
-----------------

For our contrived example, we'll build a simple registration form.

>>> import schemaish
>>> schema = schemaish.Structure()
>>> schema.add( 'firstName', schemaish.String() )
>>> schema.add( 'surname', schemaish.String() )
>>> schema.add( 'dateOfBirth', schemaish.Date() )
>>> schema.add( 'streetNumber', schemaish.Integer() )
>>> schema.add( 'country', schemaish.String() )
>>> schema.add( 'termsAndConditions', schemaish.Boolean() )
>>> form = formish.Form(schema)

As you can see, we've got strings, an integer, a data and a boolean. 

We could also have built the schema using a declarative style

>>> class MySchema(schemaish.Structure):
...     firstName = schemaish.String()
...     surname = schemaish.String()
...     dateOfBirth = schemaish.Date()
...     streetNumber = schemaish.Integer()
...     country = schemaish.String()
...     termsAndConditions = schemaish.Boolean()
>>> form = formish.Form(MySchema())

By default, all of the fields use input boxes with the date asking for isoformat and the boolean asking for True or False. We want to make the form a little friendlier though. 

We'll start with the date widget. Date parts uses three input boxes instead of a single input and, by default, is in US month first format. We're in the UK so we change dayFirst to True

>>> form['dateOfBirth'].widget = formish.DateParts(dayFirst=True)

Next we'll make the country a select box. To do this we pass a series of options to the SelectChoice widget.

>>> form['country'].widget = formish.SelectChoice(options=['UK','US'])

If we wanted different values for our options we would pass each option in as a tuple of ('value','label'). We could also set a label for the field that appears when there is no input value. This is called the 'noneOption'. The noneOptions defaults to ('', '--choose--') so we could change it to ('','Pick a Country'). Here is an example

>>> options = [('UK','I live in the UK'),('US','I live in the US')]
>>> noneOption = ('','Where do you live')
>>> form['country'].widget = formish.SelectChoice(options=options, noneOption=noneOption)

Finally, we'd like a checkbox for the Boolean value

>>> form['termsAndConditions'].widget = formish.Checkbox()

How does this form work?
------------------------

Well let's give it some default values and look at what we get. 

>>> import datetime
>>> form.defaults = {'firstName': 'Tim', 'surname': 'Parkin', 'dateOfBirth': datetime.datetime(1966,12,18), 'streetNumber': 123, 'country': 'UK', 'termsAndConditions': False}

If we create the form now, we get the following fields. One thing to note is that most widgets within Formish use strings to serialise their values into forms. The exception here is the date parts widget. 

String fields
^^^^^^^^^^^^^

This is the same as our first example but note that the label for firstName has been expanded into 'First Name'.

.. code-block:: html

    <div id="formish-firstName-field" class="field string input">
      <label for="formish-firstName">First Name</label>
      <div class="inputs">
        <input id="formish-firstName" type="text" name="firstName" value="Tim" />
      </div>
    </div>

    <div id="formish-surname-field" class="field string input">
      <label for="formish-surname">Surname</label>
      <div class="inputs">
        <input id="formish-surname" type="text" name="surname" value="Parkin" />
      </div>
    </div>

Date Field
^^^^^^^^^^

The date field splits the date into three parts, each part indicated using dotted notation.

.. raw:: html

    <div id="formish-dateOfBirth-field" class="field date dateparts">
      <label for="formish-dateOfBirth">Date Of Birth</label>
      <div class="inputs">
        <input id="formish-dateOfBirth" type="text" name="dateOfBirth.day" value="18" size="2" /> /
        <input id="formish-dateOfBirth-month" type="text" name="dateOfBirth.month" value="12" size="2" /> /
        <input id="formish-dateOfBirth-year" type="text" name="dateOfBirth.year" value="1966" size="4" />
      </div>
    </div>

.. code-block:: html

    <div id="formish-dateOfBirth-field" class="field date dateparts">
      <label for="formish-dateOfBirth">Date Of Birth</label>
      <div class="inputs">
        <input id="formish-dateOfBirth" type="text" name="dateOfBirth.day" value="18" size="2" /> /
        <input id="formish-dateOfBirth-month" type="text" name="dateOfBirth.month" value="12" size="2" /> /
        <input id="formish-dateOfBirth-year" type="text" name="dateOfBirth.year" value="1966" size="4" />
      </div>
    </div>

Integer Field
^^^^^^^^^^^^^

.. code-block:: html

    <div id="formish-streetNumber-field" class="field integer input">
      <label for="formish-streetNumber">Street Number</label>
      <div class="inputs">
        <input id="formish-streetNumber" type="text" name="streetNumber" value="123" />
      </div>
    </div>

Select Field
^^^^^^^^^^^^

This uses the 'noneOption' value to show 'Where do you live' by default but because we have set a default value, 'I live in the UK' is selected.

.. raw:: html

    <div id="formish-country-field" class="field string selectchoice">
      <label for="formish-country">Country</label>
      <div class="inputs">
        <select id="formish-country" name="country">
          <option value="">Where do you live</option>
          <option value="UK" selected="selected" >I live in the UK</option>
          <option value="US" >I live in the US</option>
        </select>
      </div>
    </div>

.. code-block:: html

    <div id="formish-country-field" class="field string selectchoice">
      <label for="formish-country">Country</label>
      <div class="inputs">
        <select id="formish-country" name="country">
          <option value="">Where do you live</option>
          <option value="UK" selected="selected" >I live in the UK</option>
          <option value="US" >I live in the US</option>
        </select>
      </div>
    </div>


Boolean Field
^^^^^^^^^^^^^

.. code-block:: html

    <div id="formish-termsAndConditions-field" class="field boolean checkbox">
      <label for="formish-termsAndConditions">Terms And Conditions</label>
      <div class="inputs">
        <input id="formish-termsAndConditions" type="checkbox" name="termsAndConditions" value="True" checked="checked"  />
      </div>
    </div>


Processing the submitted form
-----------------------------

Repeating the creation of a request using webob, setting some input values and validating gives us:

>>> import webob
>>> r = webob.Request.blank('http://localhost/', environ={'REQUEST_METHOD': 'POST'})
>>> r.POST['firstName'] = 'Tim'
>>> r.POST['surname'] = 'Parkin'
>>> r.POST['streetNumber'] = '123'
>>> r.POST['dateOfBirth.day'] = '18'
>>> r.POST['dateOfBirth.month'] = '13'
>>> r.POST['dateOfBirth.year'] = '1966'
>>> r.POST['country'] = 'UK'
>>> r.POST['termsAndConditions'] = 'True'
>>> form.validate(r)
...formish.validation.FormError: Tried to access data but conversion from request failed with 1 errors

The observant amongst you will notice I put a month of 13 in which has triggered a FormError.

Let's look at some of the error states on the form now

>>> form.errors
{'dateOfBirth': ConvertError('Invalid date: month must be in 1..12',)}

The form has a dictionary of errors on it that map to the field names.

>>> field = form.get_field('dateOfBirth')
>>> field.error
ConvertError('Invalid date: month must be in 1..12',)

The dateOfBirth field shows it's own error.

Showing the errors
------------------

The whole form is now in an error state and we can interrogate it about the errors. The form will also render itself with these errors.

>>> field.classes
'field date dateparts error'
>>> field()

This produces the following - note the error 'span' below the form field.

.. raw:: html

    <div id="formish-dateOfBirth-field" class="field date dateparts error">
      <label for="formish-dateOfBirth">Date Of Birth</label>
      <div class="inputs">
        <input id="formish-dateOfBirth" type="text" name="dateOfBirth.day" value="18" size="2" /> /
        <input id="formish-dateOfBirth-month" type="text" name="dateOfBirth.month" value="13" size="2" /> /
        <input id="formish-dateOfBirth-year" type="text" name="dateOfBirth.year" value="1966" size="4" />
      </div>
      <span class="error">Invalid date: month must be in 1..12</span>
    </div>

.. code-block:: html

    <div id="formish-dateOfBirth-field" class="field date dateparts error">
      <label for="formish-dateOfBirth">Date Of Birth</label>
      <div class="inputs">
        <input id="formish-dateOfBirth" type="text" name="dateOfBirth.day" value="18" size="2" /> /
        <input id="formish-dateOfBirth-month" type="text" name="dateOfBirth.month" value="13" size="2" /> /
        <input id="formish-dateOfBirth-year" type="text" name="dateOfBirth.year" value="1966" size="4" />
      </div>
      <span class="error">Invalid date: month must be in 1..12</span>
    </div>

Calling the 'form()' will render the whole form including the error messages.

Let's see what happens if we have an invalid integer - we'll fix the month first

>>> r.POST['dateOfBirth.month'] = '12'
>>> r.POST['streetNumber'] = 'aa'
>>> form.validate(r)
...formish.validation.FormError: Tried to access data but conversion from request failed with 1 errors
>>> field = form.get_field('streetNumber')
>>> field.error
ConvertError('Not a valid number',)
>>> 

Finally, lets see what valid data gives us.. 

>>> r.POST['streetNumber'] = '123'
>>> form.validate(r)
{'termsAndConditions': True, 'surname': u'Parkin', 'firstName': u'Tim', 'country': u'UK', 'dateOfBirth': datetime.date(1966, 12, 18), 'streetNumber': 123}





Validation
==========

Validation in Formish uses simple callable validators that raise exceptions if validation fails (Either a formish.FieldValidationError or a validatish.Invalid exception.

How Validators Work
-------------------

There is a library of validators called Validatish that has most of the typical examples you might need. Let's take a look at a simple integer validator.

.. code-block:: python

    def is_string(v):
        msg = "must be a string"
        if not isinstance(v,basestring):
            raise Invalid(msg)

the String validater get's called and raises an exception if the value is not an instance of 'basestring'. Lets take a look at another validator

.. note:: 
  
    Actual validators should not raise errors when None is passed. This is to make sure non-required fields don't raise errors if they are left empty.

Here we have an integer validator. This tries to convert the value to an integer and if it fails, raises an exception.

.. code-block:: python

    def is_integer(v):
        if v is None:
            return
        msg = "must be an integer"
        try:
            if v != int(v):
                raise Invalid(msg)
        except (ValueError, TypeError):
            raise Invalid(msg)

Let's see this one in action

>>> schema = schemaish.Structure()
>>> schema.add( 'myfield', schemaish.Integer(validator=validatish.is_integer) )
>>> form = formish.Form(schema)
>>> r = webob.Request.blank('http://localhost/', environ={'REQUEST_METHOD': 'POST'})
>>> r.POST['myfield'] = 'aa'
>>> form.validate(r)
...formish.validation.FormError: Tried to access data but conversion from request failed with 1 errors

>>> form.errors
{'myfield': ConvertError('Not a valid number',)}

Whilst it is perfectly acceptable to use functions for validation, our main library uses classes to aid type checking (for example to find out if our field is required for css styling) and in order to pass validator configuration.

The validatish library is split up into two main modules, validate and validator. Validate contains the functions that do the actual validation. Validators are class wrappers around the functions.

For example, here is our required validation function and validator


.. code-block:: python

    def is_required(v):
        if not v and v != 0:
            raise Invalid("is required")

.. code-block:: python

    class Required(Validator):
        """ Checks that the value is not empty """

        def __call__(self, v):
            validate.is_required(v)

The Required validator is sub-classing Validator but this is just an interface class (i.e. just documents the necessary methods - in this case just __call__)

So the validator is a callable and it uses the python 'non_zero' check so see if we have a value. Obviously we have to let zero through because if we're asking for an integer, zero is a valid answer; However, an empty string, empty list or None is invalid.

.. note:: The Required validator must be sub-classed if you want to create your own required validator. This is to ensure that formish inserts the appropriate css to mark up the required form fields


File Uploads 
============

Short Version
-------------

We handle files for you so that all you have to do is process the file handle given to you.. Here is an example using the default filehandlers..

>>> schema = schemaish.Structure()
>>> schema.add( 'myfile', schemaish.File )
>>> form = formish.Form(schema)
>>> from formish import filehandler
>>> form['myfile'].widget = formish.FileUpload(fileHandler=filehandler.TempFileHandlerWeb())

What does this produce?
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: html

    <div id="formish-myfile-field" class="field type fileupload">
      <label for="formish-myfile">Myfile</label>
      <div class="inputs">
        <input id="formish-myfile-remove" type="checkbox" name="myfile.remove" value="true" />
        <input id="formish-myfile-id" type="hidden" name="myfile.name" value="" />
        <input id="formish-myfile-default" type="hidden" name="myfile.default" value="" />
        <input id="formish-myfile" type="file" name="myfile.file" />
      </div>
    </div>

and looks like

.. raw:: html 

    <div id="formish-myfile-field" class="field type fileupload">
      <label for="formish-myfile">Myfile</label>
      <div class="inputs">
        <input id="formish-myfile-remove" type="checkbox" name="myfile.remove" value="true" />
        <input id="formish-myfile-id" type="hidden" name="myfile.name" value="" />
        <input id="formish-myfile-default" type="hidden" name="myfile.default" value="" />
        <input id="formish-myfile" type="file" name="myfile.file" />
      </div>
    </div>

The checkbox is included to allow you to remove a file if necessary. 

How does this return a file to me?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You will get a schemaish.type.File object back which looks like this

.. code-block:: python

    class File(object):

        def __init__(self, file, filename, mimetype):
            self.file = file
            self.filename=filename
            self.mimetype=mimetype

Where file is a file like object, filename is the original filename and the mimetype is worked out from the file suffix. All you have to do is ``.read()`` from the file attribute to get the contents.

Longer Version
--------------

File uploads are quite often the most difficult aspect of form handling. Formish has tried to make some pragmatic decisions that should ease this process for you. The first of these decisions is what type of data to use to store a file. Because we are using webob, files that arrive in formish do so in FieldStorage representation.

Upload File Temporary Storage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Formish tries to ensure that fields are 'symmetric'. i.e. what goes in comes back out in the same format). For text fields this is quite simple but for a file upload things are a little more difficult. What formish does is to use a temporary store in order to save the file in a secure location for access later. You can implement this store if you wish, using sessions or databaseses, etc. Here is the signature for a filehandler..

.. code-block:: python

    class FileHandlerMinimal(object):
        """ Example of File handler for formish file upload support. """

        def store_file(self, fs):
            """ Method to store a file """

        def get_path_for_file(self, filename):
            """ Method to get a path for a file on disk """

As you can see, the two important things are a method to store the file and a method to get the file back off disk given the filename. 

Our tempfile handler implements this as follows.

.. code-block:: python

    class TempFileHandler(FileHandlerMinimal):
        """
        File handler using python tempfile module to store file
        """

        def store_file(self, fs):
            fileno, filename = tempfile.mkstemp(suffix='%s-%s'%(uuid.uuid4().hex,fs.filename))
            fp = os.fdopen(fileno, 'wb')
            fp.write(fs.value)
            fp.close()
            prefix = tempfile.gettempprefix()
            tempdir = tempfile.gettempdir()
            filename = ''.join( filename[(len(tempdir)+len(prefix)+1):] )
            return filename

        def get_path_for_file(self, filename):
            prefix = tempfile.gettempprefix()
            tempdir = tempfile.gettempdir()
            return '%s/%s%s'%(tempdir,prefix,filename)

.. note:: We also implement a ``get_mimetype`` method that helps in building the schemaish.type.File

We typically want to access the file again from our widget however (especially in the case of image uploads!). Formish extends the TempFileHandler with a get_url_for_file method as follows..

.. code-block:: python

    class TempFileHandlerWeb(TempFileHandler):

        def __init__(self, default_url=None,
                     resource_root='/filehandler',urlfactory=None):
            self.default_url = default_url
            self.resource_root = resource_root
            self.urlfactory = urlfactory

        def get_url_for_file(self, object):
            if self.urlfactory is not None:
                return self.urlfactory(object)
            if id is None:
                return self.default_url.replace(' ','+')
            else:
                return '%s/%s'%(self.resource_root,object)

This needs configuring with a resource root (where to find files), a default_url (if we have no file, what to use - useful to showing missing images) and a urlfactory (how to convert a object into a url representation). 

So what happens when a file is uploaded?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If we're using the TempFileHandlerWeb handler the following steps take place.

.. note:: we'll presume that the first form submit has a missing field and so the form gets redisplayed.

The first time a file is uploaded, formish takes the FieldStorage object and copies the contents of the file to a tempfile using it's ``store_file`` method. 

When the form page is redisplayed, the widget uses the handlers ``get_url_for_file``` method to work out a url for the file. The file can then be displayed.

.. note:: We're not covering how the file is actually displayed. This is framework specific but we'll give an example for restish after this section.

When the users completes the corrections to the form and resubmits, formish processes the file. It first checks to see if the file is new (the widget stores a reference to the old file so it can check) and if it isn't new, it returns a schema.type.File object with None for all of the attributes.

If there is no file (i.e. no file was submitted on a clean form or a file was removed using the checkbox) then a None is returned.

If the file is new or has changed, formish generates the schemaish.type.File object from the data stored in the temporary file.

What else can I configure?
^^^^^^^^^^^^^^^^^^^^^^^^^^

The formish ``FileUpload`` widget takes the following arguments

.. automethod:: formish.widgets.FileUpload.__init__











Sequences
=========

Formish also handles sequences in fields, the basic example of this is the checkbox and the multi-select. However formish can also handle sequences in text areas and also sequences in separate fields. 

Checkbox Multi Choice
---------------------

Now we've talked through the basics.. I'll skip a lot of the detail and just demonstrate the process.. 

>>> schema = schemaish.Structure()
>>> schema.add( 'myfield', schemaish.Sequence(schemaish.Integer()) )
>>> form = formish.Form(schema)
>>> form.defaults = {'myfield': [2,4]}
>>> form['myfield'].widget = formish.CheckboxMultiChoice(options=[1,2,3,4])

Let's take a look at the html that produced.. 

.. raw:: html

    <div id="formish-myfield-field" class="field sequence checkboxmultichoice">
      <label for="formish-myfield">Myfield</label>
      <div class="inputs">
        <input id="formish-myfield-0" name="myfield" type="checkbox" value="1" />
        <label for="formish-myfield-0">1</label>
        <br />
        <input id="formish-myfield-1" name="myfield" type="checkbox" value="2" checked="checked" />
        <label for="formish-myfield-1">2</label>
        <br />
        <input id="formish-myfield-2" name="myfield" type="checkbox" value="3" />
        <label for="formish-myfield-2">3</label>
        <br />
        <input id="formish-myfield-3" name="myfield" type="checkbox" value="4" checked="checked" />
        <label for="formish-myfield-3">4</label>
        <br />
      </div>
    </div>
.. code-block:: html

    <div id="formish-myfield-field" class="field sequence checkboxmultichoice">
      <label for="formish-myfield">Myfield</label>
      <div class="inputs">
        <input id="formish-myfield-0" name="myfield" type="checkbox" value="1" />
        <label for="formish-myfield-0">1</label>
        <br />
        <input id="formish-myfield-1" name="myfield" type="checkbox" value="2" checked="checked" />
        <label for="formish-myfield-1">2</label>
        <br />
        <input id="formish-myfield-2" name="myfield" type="checkbox" value="3" />
        <label for="formish-myfield-2">3</label>
        <br />
        <input id="formish-myfield-3" name="myfield" type="checkbox" value="4" checked="checked" />
        <label for="formish-myfield-3">4</label>
        <br />
      </div>
    </div>

Select Multi Choice
-------------------

.. warning:: Not implemented yet

Text Area Sequence
------------------

Sometimes it's easier to enter information directly into a textarea

>>> form['myfield'].widget = formish.TextArea()

Which produces a simple text area as html. When it processes this textarea, it uses the csv module to get the data (it also uses it to put the default data onto the form). By default, the conversion uses commas for a simple sequence. e.g.

>>> form.defaults = {'myfield': [1,3,5,7]}

.. raw:: html

    <div id="formish-myfield-field" class="field sequence textarea">
      <label for="formish-myfield">Myfield</label>
      <div class="inputs">
        <textarea id="formish-myfield" name="myfield">1,3,5,7</textarea>
      </div>
    </div>


.. code-block:: html

    <div id="formish-myfield-field" class="field sequence textarea">
      <label for="formish-myfield">Myfield</label>
      <div class="inputs">
        <textarea id="formish-myfield" name="myfield">1,3,5,7</textarea>
      </div>
    </div>

However you can change this behaviour by passing the Textarea widget a converter_option dictionary value .. e.g.


>>> form['myfield'].widget = formish.TextArea(converter_options={'delimiter': '\n'})

.. raw:: html

    <textarea id="formish-myfield" name="myfield">1
  3
  5
  7</textarea>

.. code-block:: html

    <textarea id="formish-myfield" name="myfield">1\n3\n5\n7</textarea>

Text Area Sequence of Sequences
-------------------------------

You can also use a textarea to represent a sequence of sequences... 

>>> schema = schemaish.Structure()
>>> schema.add( 'myfield', schemaish.Sequence(schemaish.Sequence(schemaish.Integer())))
>>> form = formish.Form(schema)
>>> form.defaults = {'myfield': [[2,4],[6,8]]}
>>> form['myfield'].widget = formish.TextArea()

In this case, the default delimiter is a comma and is used on a row by row basis.

.. raw:: html

    <textarea id="formish-myfield" name="myfield">2,4
  6,8</textarea>

.. code-block:: html

    <textarea id="formish-myfield" name="myfield">2,4\n6,8</textarea>

Multiple Input Fields
---------------------

.. warning:: This code hasn't settled down yet, please check for updates.

If you just pass a sequence to a form without any widgets, a jquery powered sequence editor will be used. This will allow you to add and remove the fields within the sequence. Check the 'testish' application for more details.

Nested Form Structures
======================

Formish also allows you to create sub-sections in forms that can contain any other valid form part. We'll use an address and name section to expand out registration form.

A Structure of Structures
-------------------------

>>> class MyName(schemaish.Structure):
...     firstName = schemaish.String()
...     surname = schemaish.String()
>>> class MyAddress(schemaish.Structure):
...     streetNumber = schemaish.Integer()
...     country = schemaish.String()
>>> class MySchema(schemaish.Structure):
...     name = MyName()
...     address = MyAddress()
...     termsAndConditions = schemaish.Boolean()
>>> form = formish.Form(MySchema())

This will create the following

.. raw:: html


    <form id="formish" action="" method="post" enctype="multipart/form-data" accept-charset="utf-8">
      <input type="hidden" name="_charset_" />
      <input type="hidden" name="__formish_form__" value="formish" />
      <fieldset id="formish-name-field" class="field myname sequencedefault sequencecontrols">
        <legend>Name</legend>
        <div id="formish-name-firstName-field" class="field string input">
          <label for="formish-name-firstName">First Name</label>
          <div class="inputs">
            <input id="formish-name-firstName" type="text" name="name.firstName" value="" />
          </div>
        </div>
        <div id="formish-name-surname-field" class="field string input">
          <label for="formish-name-surname">Surname</label>
          <div class="inputs">
            <input id="formish-name-surname" type="text" name="name.surname" value="" />
          </div>
        </div>
      </fieldset>
      <fieldset id="formish-address-field" class="field myaddress sequencedefault sequencecontrols">
        <legend>Address</legend>
        <div id="formish-address-streetNumber-field" class="field integer input">
          <label for="formish-address-streetNumber">Street Number</label>
          <div class="inputs">
            <input id="formish-address-streetNumber" type="text" name="address.streetNumber" value="" />
          </div>
        </div>
        <div id="formish-address-country-field" class="field string input">
          <label for="formish-address-country">Country</label>
          <div class="inputs">
            <input id="formish-address-country" type="text" name="address.country" value="" />
          </div>
        </div>
      </fieldset>
      <div id="formish-termsAndConditions-field" class="field boolean input">
        <label for="formish-termsAndConditions">Terms And Conditions</label>
        <div class="inputs">
          <input id="formish-termsAndConditions" type="text" name="termsAndConditions" value="" />
        </div>
      </div>
      <div class="actions">
        <input type="submit" id="formish-action-submit" name="submit" value="Submit" />
      </div>
    </form>

.. code-block:: html

    <form id="formish" action="" method="post" enctype="multipart/form-data" accept-charset="utf-8">
      <input type="hidden" name="_charset_" />
      <input type="hidden" name="__formish_form__" value="formish" />
      <fieldset id="formish-name-field" class="field myname sequencedefault sequencecontrols">
        <legend>Name</legend>
        <div id="formish-name-firstName-field" class="field string input">
          <label for="formish-name-firstName">First Name</label>
          <div class="inputs">
            <input id="formish-name-firstName" type="text" name="name.firstName" value="" />
          </div>
        </div>
        <div id="formish-name-surname-field" class="field string input">
          <label for="formish-name-surname">Surname</label>
          <div class="inputs">
            <input id="formish-name-surname" type="text" name="name.surname" value="" />
          </div>
        </div>
      </fieldset>
      <fieldset id="formish-address-field" class="field myaddress sequencedefault sequencecontrols">
        <legend>Address</legend>
        <div id="formish-address-streetNumber-field" class="field integer input">
          <label for="formish-address-streetNumber">Street Number</label>
          <div class="inputs">
            <input id="formish-address-streetNumber" type="text" name="address.streetNumber" value="" />
          </div>
        </div>
        <div id="formish-address-country-field" class="field string input">
          <label for="formish-address-country">Country</label>
          <div class="inputs">
            <input id="formish-address-country" type="text" name="address.country" value="" />
          </div>
        </div>
      </fieldset>
      <div id="formish-termsAndConditions-field" class="field boolean input">
        <label for="formish-termsAndConditions">Terms And Conditions</label>
        <div class="inputs">
          <input id="formish-termsAndConditions" type="text" name="termsAndConditions" value="" />
        </div>
      </div>
      <div class="actions">
        <input type="submit" id="formish-action-submit" name="submit" value="Submit" />
      </div>
    </form>


This data will come back in dictionary form.. i.e.

.. code-block:: python

  {'name': {'firstName':'Tim', 'surname':'Tim'}, 'address': {'streetNumber': 123, 'country': 'UK'}, 'termsAndConditions': True}

Other Combinations
------------------

Formish will also let you build up a sequence of structures and will use it's jquery javascript to allow you to dynamically add and remove sections. This also works when recursively nested so it is perfectly possibly to have a list of addresses, each of which has a list of phone numbers.

Tuples
------

A tuple can be used to create a list that has different types in it. For instance, if we used the Sequence of Sequence example above, we have no control over how many items are in each row. Using a Sequence of Tuples allows us to define the length of the row and also the types of the items in the row.

Lets see how that works.

>>> schema.add( 'myfield', schemaish.Sequence( schemaish.Tuple( schemaish.Integer(), schemaish.Date() ) ) )
>>> form = formish.Form(schema)
>>> form['myfield'].widget=formish.TextArea()

You will now get a textarea that will return validation messages if it is unable to convert to integers or strings and that will output appropriately typed data.































Class Documentation
===================


Form Class
----------

.. autoclass:: formish.forms.Form
  :members: action, add_action, fields, validate,__call__

Field Class
-----------

.. autoclass:: formish.forms.Field
  :members: title, description, cssname, classes, value, required, error, widget,__call__
