StringConvert Manual
++++++++++++++++++++

StringConvert is a package which provides ConversionKit converters to convert
strings to common Python types.

Understanding Unicode
=====================

Any application you are working with should deal with Unicode strings
internally. You should never work with ordinary Python strings because as soon
as someone enters a non-ASCII character in your application it is likely to
break in an unpredictable way because ordinary 8-bit Python strings can't
handle these characters.

Best practice is to always *decode* strings to Unicode objects from whatever
encoding they are in (often UTF-8) as soon as they enter your application. You
then work with Unicode throughout your application and then *encode* the
Unicode back to whatever is needed (again often UTF-8) as the string leaves
your application.

To help you use this best practice approach, most of StringConvert converters
expect Unicode objects and will raise an exception if you pass them ordinary
8-bit Python strings.

If you want to convert a Python string you need to do it in two parts. First
convert the 8-bit string to a Unicode object and then convert the Unicode
object to whatever else you need.

Here's an example showing the conversion raising an exception when performed
with a string, working with a Unicode string and then working with a normal
string again when used with the ``stringToUnicode()`` converter.

.. sourcecode :: pycon

    >>> from stringconvert import stringToUnicode, unicodeToInteger
    >>> from conversionkit import Conversion, chainConverters
    >>>
    >>> Conversion('3').perform(unicodeToInteger())
    Traceback (most recent call last):
      File ...
    StringConvertError: The value '3' is not a Unicode object
    >>> Conversion(u'3').perform(unicodeToInteger()).result
    3
    >>> Conversion('3').perform(chainConverters(stringToUnicode(encoding='US-ASCII'), unicodeToInteger())).result
    3

Core Types
==========

Converting Strings to Booleans
------------------------------

StringConvert provides the ``unicodeToBool()`` converter for converting strings
to ``True`` or ``False`` values.

.. sourcecode :: pycon

    >>> from stringconvert import unicodeToBoolean
    >>> from conversionkit import Conversion

Here are some examples:

.. sourcecode :: pycon

    >>> Conversion(u'yes').perform(unicodeToBoolean()).result
    True
    >>> Conversion(u'1').perform(unicodeToBoolean()).result
    True
    >>> Conversion(u'on').perform(unicodeToBoolean()).result
    True
    >>> Conversion(u'true').perform(unicodeToBoolean()).result
    True
    >>> Conversion(u'no').perform(unicodeToBoolean()).result
    False
    >>> Conversion(u'0').perform(unicodeToBoolean()).result
    False
    >>> Conversion(u'off').perform(unicodeToBoolean()).result
    False
    >>> Conversion(u'false').perform(unicodeToBoolean()).result
    False

All arguments must be strings or you will get an error:

.. sourcecode :: pycon

    >>> Conversion(True).perform(unicodeToBoolean()).result
    Traceback (most recent call last):
      File ...
    StringConvertError: The value True is not a Unicode object

The string argument are case-insensitive so this works too:

.. sourcecode :: pycon

    >>> Conversion(u'fAlSe').perform(unicodeToBoolean()).result
    False

You can also customise which strings are treated as true and which are treated
as False by setting ``true_values`` and ``false_values``.
 
.. sourcecode :: pycon

    >>> is_fruit = unicodeToBoolean(
    ...    true_values=[u'apple', u'pear'],
    ...    false_values=[u'potatoe', u'carrot'], 
    ... )
    >>> Conversion(u'pear').perform(is_fruit).result
    True
    >>> Conversion(u'potatoe').perform(is_fruit).result
    False

This overrides the
defaults of ``true_values=[u'yes', u'1', u'on', u'true']``,
``false_values=[u'no', u'0', u'off', u'false']``:

.. sourcecode :: pycon

    >>> Conversion(u'on').perform(is_fruit).result
    Traceback (most recent call last):
      File ...
    ConversionError: Unrecognised option u'on' for a boolean

Converting Strings to Strings
-----------------------------

It might sound a very strange thing to want to do but a string-to-string
converter can enforce a minumum or maximum length to a string (or both).

.. sourcecode :: pycon

    >>> from stringconvert import unicodeToUnicode
    >>> Conversion(u'pear').perform(unicodeToUnicode()).result
    u'pear'
    >>> Conversion(u'pear').perform(unicodeToUnicode(min=6)).error
    'The string must contain 6 characters or more'
    >>> Conversion(u'pear').perform(unicodeToUnicode(max=2)).error
    'The string must contain 2 characters or less'
    >>> Conversion(u'pear').perform(unicodeToUnicode(min=2, max=6)).result
    u'pear'

.. tip ::

   Remember that you can test whether or not a conversion is successful or not
   by accessing the ``conversion.successful`` attribute which is ``True`` if it
   was successful, ``False`` otherwise.

Converting Strings to Floats
----------------------------

Convert strings representing numbers to floats.

.. sourcecode :: pycon

    >>> from stringconvert import unicodeToFloat
    >>> Conversion(u'1.04').perform(unicodeToFloat()).result
    1.04
    >>> Conversion(u'1.04').perform(unicodeToFloat(min=6)).error
    'The number must be greater than or equal to 6'
    >>> Conversion(u'2.01').perform(unicodeToFloat(max=2)).error
    'The number must be less than or equal to 2'
    >>> Conversion(u'3.5').perform(unicodeToFloat(min=2, max=6)).result
    3.5

You can also convert strings representing integers:

.. sourcecode :: pycon

    >>> result = Conversion(u'3').perform(unicodeToFloat(min=2, max=6)).result
    >>> result
    3.0
    >>> type(result)
    <type 'float'>

Converting Strings to Integers
------------------------------

Convert strings representing integers to integers, the API is the same as the
API for converting strings to floats.

.. sourcecode :: pycon

    >>> from stringconvert import unicodeToInteger
    >>> result = Conversion(u'3').perform(unicodeToInteger(min=2, max=6)).result
    >>> result
    3
    >>> type(result)
    <type 'int'>

You can't convert floats to integers though:

.. sourcecode :: pycon

    >>> Conversion(u'1.04').perform(unicodeToInteger()).result
    Traceback (most recent call last):
      File ...
    ConversionError: invalid literal for int() with base 10: '1.04'

Converting Strings to Dates and Times
-------------------------------------

StringConvert provides ``unicodeToDatetime()``, ``unicodeToTime()`` and
``unicodeToDate()`` converters. 

.. sourcecode :: pycon

    >>> from stringconvert import unicodeToDatetime, unicodeToTime, unicodeToDate

They all behave in the same way:

.. sourcecode :: pycon

    >>> Conversion(u'2009-07-15').perform(unicodeToDate()).result
    datetime.date(2009, 7, 15)
    >>> Conversion(u'2009-07-15 14:13').perform(unicodeToDatetime()).result
    datetime.datetime(2009, 7, 15, 14, 13)
    >>> Conversion(u'14:13').perform(unicodeToTime()).result
    datetime.time(14, 13)

.. note ::

   The ``unicodeToDatetime()`` converter is not spelled ``unicodeToDateTime()``
   because a ``Datetime`` is a Python type and is spelled with a lowercase ``t``.

Each of the converters also takes a single argument called ``format``
which specifies the format the of the input strings. You can use any of the format codes
specified in the `Python time module documentation
<http://docs.python.org/library/time.html#time.strftime>`_. Here are some
examples:

.. sourcecode :: pycon

    >>> # US format dates
    >>> Conversion(u'07/15/2009').perform(unicodeToDate(format='%m/%d/%Y')).result
    datetime.date(2009, 7, 15)
    >>> # US format dates
    >>> Conversion(u'15/07/2009').perform(unicodeToDate(format='%d/%m/%Y')).result
    datetime.date(2009, 7, 15)

.. note ::

   It is easy to get the codes for ``%m`` (month) and ``%M`` (minute) muddled
   up so the ``unicodeToDate()`` converter won't let you specify ``%M`` since dates
   don't contain minutes.

Regular Expressions
===================

You can also have a converter which matches based on a regular expression:

.. sourcecode :: pycon

    >>> from stringconvert.regex import matchRegex

It is used like this:

.. sourcecode :: pycon

    >>> import re
    >>> two_words = matchRegex(
    ...     '([A-Z]+) ([A-Z]+)', 
    ...     options=[re.I],
    ...     msg_no_match="Please choose two words matching %(regex)s",
    ... )
    >>> Conversion(u'The Car').perform(two_words).result
    u'The Car'
    >>> Conversion(u'The Fast Car').perform(two_words).error
    'Please choose two words matching ([A-Z]+) ([A-Z]+)'

There are a few things to notice:

* You can use the standard ``re`` module options listed at 
  http://docs.python.org/library/re.html#module-contents to modify the
  behaviour of the regular expresion (here we used ``re.I`` to make it a 
  case insensitive match)
* You can customise the error message and include the original regular 
  expression if you want (although this wouldn't be very useful for
  user-facing messages)

You can also have the input stripped if you like:

.. sourcecode :: pycon

    >>> two_words_stripped = matchRegex(
    ...     '([A-Z]+) ([A-Z]+)', 
    ...     strip=True,
    ...     options=[re.I],
    ...     msg_no_match="Please choose two words matching %(regex)s",
    ... )
    >>> Conversion(u' The Car ').perform(two_words).error
    'Please choose two words matching ([A-Z]+) ([A-Z]+)'
    >>> Conversion(u' The Car ').perform(two_words_stripped).result
    u'The Car'

Email Handling
==============

Here are some tests for the ``unicodeToEmail()`` converter.  

First some imports:

.. sourcecode :: pycon

    >>> from conversionkit import Conversion
    >>> from stringconvert.email import unicodeToEmail

The examples below demonstrate the behaviour and errors without the domain
resolution enabled:

.. sourcecode :: pycon

    >>> e = unicodeToEmail()
    >>> Conversion(u' test@foo.com ').perform(e).result
    u'test@foo.com'
    >>> Conversion(u'test').perform(e).error
    u'An email address must contain a @ character'
    >>> Conversion(u'test@domain@com').perform(e).error
    u'An email address must contain only one @ character'
    >>> Conversion(u'test@foobar').perform(e).error
    u'The domain portion of the email address is invalid (the portion after the @: foobar)'
    >>> Conversion(u'test@foobar.com.5').perform(e).error
    u'The domain portion of the email address is invalid (the portion after the @: foobar.com.5)'
    >>> Conversion(u'test@foo..bar.com').perform(e).error
    u'The domain portion of the email address is invalid (the portion after the @: foo..bar.com)'
    >>> Conversion(u'test@.foo.bar.com').perform(e).error
    u'The domain portion of the email address is invalid (the portion after the @: .foo.bar.com)'
    >>> Conversion(u'nobody@xn--m7r7ml7t24h.com').perform(e).result
    u'nobody@xn--m7r7ml7t24h.com'
    >>> Conversion(u'o*reilly@test.com').perform(e).result
    u'o*reilly@test.com'

Now let's try with domain resolution. This will fail unless you have PyDNS
installed.

.. sourcecode :: pycon

    >>> e = unicodeToEmail(resolve_domain=True)
    >>> Conversion(u'doesnotexist@jimmyg.org').perform(e).result
    u'doesnotexist@jimmyg.org'
    >>> Conversion(u'test@thisdomaindoesnotexistithinkforsure.com').perform(e).error
    u'The domain of the email address does not exist (the portion after the @: thisdomaindoesnotexistithinkforsure.com)'
    >>> Conversion(u'test@google.com').perform(e).result
    u'test@google.com'

.. tip ::

    The examples above doesn't work from my home computer because I believe my
    ISP might be doing something strange. If you can't get a sensible result 
    from the ``dig`` command, the DNS resolution above will not work even with 
    PyDNS installed. Here's the ``dig`` command failing on my machine:

    ::
        $ dig google.com MX
    
        ; <<>> DiG 9.5.1-P2 <<>> google.com MX
        ;; global options:  printcmd
        ;; connection timed out; no servers could be reached

    Here it is working when run on a real server:

    ::    
        james@ve2:~$ dig google.com MX
        
        ; <<>> DiG 9.5.1-P1 <<>> google.com MX
        ;; global options:  printcmd
        ;; Got answer:
        ;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 35418
        ;; flags: qr rd ra; QUERY: 1, ANSWER: 6, AUTHORITY: 0, ADDITIONAL: 0
        
        ;; QUESTION SECTION:
        ;google.com.			IN	MX
        
        ;; ANSWER SECTION:
        google.com.		766	IN	MX	100 smtp2.google.com.
        google.com.		766	IN	MX	10 google.com.s9a2.psmtp.com.
        google.com.		766	IN	MX	10 google.com.s9b1.psmtp.com.
        google.com.		766	IN	MX	10 google.com.s9b2.psmtp.com.
        google.com.		766	IN	MX	100 smtp1.google.com.
        google.com.		766	IN	MX	10 google.com.s9a1.psmtp.com.
        
        ;; Query time: 0 msec
        ;; SERVER: 213.133.98.98#53(213.133.98.98)
        ;; WHEN: Wed Sep 30 11:40:06 2009
        ;; MSG SIZE  rcvd: 206

Lists of Email Addresses
------------------------

StringConvert also comes with a tool which attempts to parse well-formed lists
of email addresses separated by a ``,``, ``;`` or end of line character. It
will attempt to parse the firstname, lastname and organisation as well as the
email itself. It doesn't validate the individual email addresses and shouldn't
be considered 100% robust.

Here's an example. First the imports:

.. sourcecode :: pycon

    >>> from conversionkit import Conversion
    >>> from stringconvert.email import listOfEmails

Here's our test string:

.. sourcecode :: pycon

    >>> email_list = u'James Gardner <james@example.com>; Richard Edward Jones < richard.e.jones@example.org>; kevin@example.net;'

Let's extract the addresses:

.. sourcecode :: pycon

    >>> print Conversion(email_list).perform(listOfEmails()).result
    [{'email': u'james@example.com', 'name': u'James Gardner'}, {'email': u'richard.e.jones@example.org', 'name': u'Richard Edward Jones'}, {'email': u'kevin@example.net', 'name': u'kevin'}]

Here's an example, splitting the names into parts and guessing the organisation
from the domain:

.. sourcecode :: pycon

    >>> print Conversion(email_list).perform(
    ...     listOfEmails(split_name=True, extract_organisation=True)
    ... ).result
    [{'lastname': u'Gardner', 'organisation': u'Example', 'email': u'james@example.com', 'firstname': u'James', 'middlenames': u''}, {'lastname': u'Jones', 'organisation': u'Example', 'email': u'richard.e.jones@example.org', 'firstname': u'Richard', 'middlenames': u'Edward'}, {'lastname': u'', 'organisation': u'Example', 'email': u'kevin@example.net', 'firstname': u'Kevin', 'middlenames': u''}]

Stripping Input
===============

The ``unicodeToBoolean()``, ``unicodeToDate()``, ``unicodeToDatetime()``,
``unicodeToDate()``, ``unicodeToEmail()`` functions take an optional ``strip``
argument which defaults to ``True`` and causes the conversion input to be
stripped of leading and trailing whitespace. The ``matchRegex()`` has a similar
``strip`` argument but it defaults to ``False``.  ``unicodeToUnicode()`` doesn't
have a ``strip`` option and doesn't strip input. ``unicodeToFloat()`` and
``unicodeToInteger()`` don't have a ``strip`` argument but always strip input as
this is the standard Python behaviour for such conversions:

.. sourcecode :: pycon

    >>> int(' 12 ')
    12

Here is an example:

.. sourcecode :: pycon

    >>> Conversion(u' true ').perform(unicodeToBoolean()).result
    True
    >>> Conversion(u' true ').perform(unicodeToBoolean(strip=False)).result
    Traceback (most recent call last):
      File ...
    ConversionError: Unrecognised option u' true ' for a boolean

