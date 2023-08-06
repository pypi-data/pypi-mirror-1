mvc
===========================================================

.. module:: smisk.mvc
.. versionadded:: 1.1.0

Model-View-Controller-based sub-framework.

This module and it's sub-modules constitutes the most common way of
using Smisk, mapping URLs to the *control tree* – an actual class
tree, growing from :class:`smisk.mvc.control.Controller`.

**Key members**

* :func:`main()` is a helper function which facilitates the most common use
  case: Setting up an application, configuring it, running it and
  logging uncaught exceptions.

* The :class:`Application` class is the type of application. Normally you do
  not subclass :class:`Application`, but rather configure it and its
  different components.

* The :mod:`smisk.mvc.console` module is an interactive console, aiding in
  development and management.

* The :mod:`smisk.mvc.control` module contains many useful functions for inspecting
  the *control tree*.

**Example**::

  from smisk.mvc import *
  class root(Controller):
    def __call__(self, *args, **params):
     return {'message': 'Hello World!'}

  main()


Configuration parameters
-------------------------------------------------

.. describe:: smisk.mvc.response.serializer

  Name of a default response serializer.
  
  The value should be the name of a serializer *extension* (the value should be a valid key in the :attr:`smisk.serialization.serializers.extensions <smisk.serialization.Registry.extensions>` dictionary).
  
  If not set, the :attr:`Response.fallback_serializer` will be used for clients not requesting 
  any particular content type.
  
  :default: :samp:`None`
  :type: str


.. describe:: smisk.mvc.etag

  Enables adding an ETag header to all buffered responses.

  The value needs to be either the name of a valid hash function
  in the ``hashlib`` module (i.e. "md5"), or a something respoding
  in the same way as the hash functions in hashlib. i.e. need to
  return a hexadecimal string rep when:
  
  .. code-block:: python

    h = etag(data)
    h.update(more_data)
    etag_value = h.hexdigest()
  
  Enabling this is generally *not recommended* as it introduces a
  small to moderate performance hit, because a checksum need to be
  calculated for each response, and because of the nature of the data
  Smisk does not know about all stakes in a transaction,
  thus constructing a valid ETag might somethimes be impossible.

  :default: :samp:`None`
  :type: str


.. describe:: smisk.mvc.strict_tcn

  Controls whether or not this application is strict about
  transparent content negotiation.

  For example, if this is ``True`` and a client accepts a
  character encoding which is not available, a 206 Not Acceptable
  response is sent. If the value would have been ``False``, the
  response would be sent using a data encoder default character
  set.

  This affects ``Accept*`` request headers which demands can not
  be met.

  As HTTP 1.1 (RFC 2616) allows fallback to defaults (though not
  recommended) we provide the option of turning off the 206
  response. Setting this to false will cause Smisk to encode text
  responses using a best-guess character encoding.

  :default: :samp:`True`
  :type: bool



Leaf filters
-------------------------------------------------

A *leaf filter* is basically code that is run prior to and after calling a leaf on the controller tree, allowing manipulation of input, output and the states of things.

Let's have a look at an example filter which gives the ability to say "this leaf requires a logged in user"::
  
  from smisk.mvc.decorators import leaf_filter
  
  @leaf_filter
  def require_login(leaf, *va, **kw):
    if not request.session or not request.session.get('userid'):
      redirect_to(root.login)
    return leaf(*va, **kw)

This filter requires a valid session and the key ``userid`` to be set in the session (in this case things are simplified for educational reasons --- in reality we would probably check the type of the session object also).

And here is how you would use the filter above::

  class root(Controller):
    @require_login
    def protected(self):
      return {'secret launch codes': [u'abc', 123]}
    
    def login(self):
      pass # (actual auth code here)
  
  # curl localhost:8080/protected
  # 302 Found -> http://localhost:8080/login

Note that the :samp:`from smisk.mvc.decorators import leaf_filter` is not needed if you are importing everything from :mod:`smisk.mvc` since ``leaf_filter`` is also exported from :mod:`smisk.mvc`.

For more information and examples see :mod:`smisk.mvc.filters` and 
:func:`smisk.mvc.decorators.leaf_filter`.



Functions
-------------------------------------------------

.. function:: environment() -> string

  Name of the current environment.

  Returns the value of ``SMISK_ENVIRONMENT`` environment value and
  defaults to "``stable``".


.. function:: main(application=None, appdir=None, bind=None, forks=None, handle_errors=True, cli=True, *args, **kwargs) -> object

  Helper for setting up and running an application.
  
  This function is not a true function, but rather an instance of :class:`Main`.
  
  See documentation of :func:`smisk.util.main.main()` for more information.


.. function:: run(bind=None, application=None, forks=None, handle_errors=False) -> object

  Helper for running an application.

  Note that because of the nature of ``libfcgi`` an application can
  not  be started, stopped and then started again. That said, you can
  only start  your application once per process. (Details:
  OS_ShutdownPending sets a  process-wide flag causing any call to
  accept to bail out)

  **Environment variables**

  .. envvar:: SMISK_BIND
  
    If set and not empty, a call to ``smisk.core.bind`` will occur,
    passing the value to bind, effectively starting a stand-alone
    process.
  
  :param bind:
    Bind to address (and port). Note that this overrides ``SMISK_BIND``.
  :param application:
    An application type or instance.
  :param forks:
    Number of child processes to spawn.
  :param handle_errors:
    Handle any errors by wrapping calls in :func:`smisk.util.main.handle_errors_wrapper()`
  :Returns:
    Anything returned by :meth:`Application.run()`
  :rtype:
    object
  :See:
    :func:`setup()`, :func:`main()`


.. function:: setup(application=None, appdir=None, *args, **kwargs) -> Application

  :deprecated: You should use :meth:`smisk.util.main.Main.setup()` instead.
  
  
  
  

Classes
-------------------------------------------------


.. class:: Main(smisk.util.main.Main)
  
  :see: Documentation of :class:`smisk.util.main.Main`


.. class:: Application(smisk.core.Application)

  MVC application
  
  :see: :class:`smisk.core.Application`


  .. attribute:: templates
  
    Templates handler.
  
    If this evaluates to false, templates are disabled.
  
    :see: `__init__()`
    :type: Templates

  
  .. attribute:: routes
  
    Router.
  
    :type: Router

  
  .. attribute:: serializer
  
    Used during runtime.
    Here because we want to use it in error()
  
    :type: Serializer

  
  .. attribute:: destination

    Used during runtime.
    Available in actions, serializers and templates.
  
    :type: routing.Destination

  
  .. attribute:: template

    Used during runtime.
  
    :type: mako.template.Template

  
  .. attribute:: unicode_errors
  
    How to handle unicode conversions.
  
    Possible values: ``strict, ignore, replace, xmlcharrefreplace, backslashreplace``
  
    :type: string
  
  
  .. attribute:: autoclear_model_session
  
    Automatically clear the model session cache before each request is handled.
  
    You should not disable this unless any of the following statements apply:
  
    * You do not use smisk.model or SQLAlchemy at all (no database).
  
    * You run only one process (safe to cache).
  
    * Your application only reads a set of data that never changes.
  
    * Your model does not involve entity relations.
  
    Disabling this means entities stay in the local memory cache between sessions.
    (Relations and their content etc are cached, but not the actual data in the entities)
  
    Consider this model::
  
      class Department(Entity):
        people = OneToMany('Person')
    
      class Person(Entity):
        department = ManyToOne('Department')
  
    Now, imagine we have two processes running; process A and process B. Process A gets a request to add a new person to an existing department. Afterwards, process B is requested to list all people in the same department. Now, if autoclear_model_session where set to False, the previously added person would no show up in the listing of people in the department which process B queried. This is because which people is "contained within" what department has been implicitly cached by SQLAlchemy.
  
    :type: ``bool``
    :default: ``True``

  
  
  .. attribute:: leaf_filters
    
    Application-global leaf filters, applied to all leafs in the controller tree.
    
    The filter are applied in the order they appear in this list.
    
    .. code-block:: python
    
      from smisk.mvc import *
    
      @leaf_filter
      def ensure_page_title(leaf, *va, **kw):
        rsp = leaf(*va, **kw)
        rsp.setdefault('title', u'The Title')
        return rsp
    
      class App(Application):
        def application_will_start(self):
          self.leaf_filters.append(ensure_page_title)
          return Application.application_will_start(self)
    
    :type: ``list``
    
    .. versionadded:: 1.1.3
  
  
  
  

  .. method:: __init__(router=None, templates=None, show_traceback=False, *args, **kwargs)
  
    TODO


  .. method:: run()
  
    TODO


  .. method:: application_did_stop()
  
    TODO


  .. method:: application_will_start()
  
    TODO


  .. method:: apply_leaf_restrictions()

    Applies any restrictions set by the current action.


  .. method:: autoload_configuration(config_mod_name='config')

    Automatically load configuration from application sub-module
    named *config_mod_name*.

    :param config_mod_name:
      Name of the application configuration sub-module


  .. method:: call_action(args, params) -> dict

    Resolves and calls the appropriate action, passing args and
    params to it.

    :Returns:
      Response structure or None


  .. method:: encode_response(rsp) -> str

    Encode the response object *rsp*

    :param rsp:
      Must be a string, a dict or None
    :Returns:
      *rsp* encoded as a series of bytes
    :See:
      :meth:`send_response()`


  .. method:: error(typ, val, tb)

    Handle an error and produce an appropriate response.

    :param typ:
      Exception type
    :param val:
      Exception value
    :param tb:
      Traceback


  .. method:: parse_request()

      Parses the request, involving appropriate serializer if needed.

      :Returns:
        (list arguments, dict parameters)
      :rtype: tuple


  .. method:: response_serializer(no_http_exc=False) -> Serializer

    Return the most appropriate serializer for handling response
    encoding.

    :param no_http_exc:
      If true, HTTP statuses are never
      rised when no acceptable  serializer is found. Instead a
      fallback serializer will be returned: First we try to
      return a serializer for format html, if that fails we
      return the first registered serializer. If that also fails
      there is nothing more left to do but return None. Primarily
      used by *error()*.
    :Returns:
      The most appropriate serializer
    :rtype:
      :class:`smisk.serialization.Serializer`


  .. method:: send_response(rsp)

    Send the response to the current client, finalizing the current
    HTTP transaction.

    :param rsp:
      Response body
    :See:
      :meth:`encode_response()`


  .. method:: service()
   
     Manages the life of a HTTP transaction.
   
     **Summary**
   
     #. Reset current shared *request*, *response* and *self*.
   
     #. Aquire response serializer from *response_serializer()*.
   
        #. Try looking at ``response.format``, if set.
      
        #. Try looking at any explicitly set ``Content-Type`` in
           *response*.
      
        #. Try looking at request filename extension, derived from
           ``request.url.path``.
      
        #. Try looking at media types in request ``Accept`` header.
      
        #. Use *Response.fallback_serializer* or raise
           *http.MultipleChoices*, depending on value of
           ``no_http_exc`` method argument.
   
     #. Parse request using *parse_request()*.
   
        #. Update request parameters with any query string
           parameters.
      
        #. Register for the client acceptable character encodings by
           looking  at any ``Accept-Charset`` header.
      
        #. Update request parameters and arguments with any POST
           body, possibly by using a serializer to decode the request
           body.
   
     #. Resolve *controller leaf* by calling *routes*.
   
        #. Apply any route filters.
      
        #. Resolve *leaf* on the *controller tree*.
   
     #. Apply any format restrictions defined by the current
        *controller leaf*.
   
     #. Append ``Vary`` header to response, with the value
        ``negotiate, accept, accept-charset``.
   
     #. Call the *controller leaf* which will return a *response
        object*.
   
        #. Applies any "before" filters.
      
        #. Calls the *controller leaf*
      
        #. Applies any "after" filters.
   
     #. Flush the model/database session, if started or modified,
        committing any modifications.
   
     #. If a templates are used, and the current *controller leaf* is
        associated  with a template – aquire the template object for
        later use in  *encode_response()*.
   
     #. Encode the *response object* using *encode_response()*,
        resulting in a string of opaque bytes which constitutes the
        response body, or payload.
   
        #. If the *response object* is ``None``, either render the
           current template (if any) without any parameters or fall
           back to *encode_response()*  returning ``None``.
      
        #. If the *response object* is a string, encode it if needed
           and simply return the string, resulting in the input to
           *encode_response()* compares equally to the output.
      
        #. If a template object has been deduced from previous
           algorithms,  serialize the *response object* using that
           template object.
      
        #. Otherwise, if no template is used, serialize the *response
           object* using the previously deduced response serializer.
     
     #. Complete (or commit) the current HTTP transaction by sending
        the response by calling *send_response()*.
      
        #. Set ``Content-Length`` and other response headers, unless
           the response has already begun.
      
        #. Calculate *ETag* if enabled through the *etag* attribute.
      
        #. Write the response body.


  .. method:: setup()

    Setup application state.

    Can be called multiple times and is automatically called, just
    after calling *autoload_configuration()*, by *setup()*
    and *application_will_start()*.

    **Outline**

    1. If *etag* is enabled and is a string, replaces *etag* with
       the named hashing algorithm from hashlib.

    2. If *templates* are enabled but ``templates.directories``
       evaluates to false, set ``templates.directories`` to the
       default ``[SMISK_APP_DIR + "templates"]``.

    3. Make sure *Response.fallback_serializer* has a valid
       serializer as it's value.

    4. Setup any models.


  .. method:: template_for_path(path) -> Template

    Aquire template URI for *path*.

    :param path:
      A relative path
    :rtype:
      :class:`template.Template`


  .. method:: template_for_uri(uri) -> Template

    Aquire template for *uri*.

    :param uri:
      Path
    :rtype:
      :class:`template.Template`


  .. method:: template_uri_for_path(path) -> string

    Get template URI for *path*.

    :param path:
      A relative path
    :rtype:
      string



.. ------------------------------------------------------------------------------------------



.. class:: Request(smisk.core.Request)


  .. attribute:: serializer

    Serializer used for decoding request payload.
  
    Available during a HTTP transaction.
  
    :type: smisk.serialization.Serializer


  .. attribute:: cn_url
    
    .. versionadded:: 1.1.3
    
    URL with any filename extension removed, for use with Content
    Negotiation.
    
    If the request did not contain a filename extension, this is the same
    object as :attr:`smisk.core.Request.url`.
    
    :type: :class:`smisk.core.URL`



.. ------------------------------------------------------------------------------------------



.. class:: Response(smisk.core.Response)


  .. attribute:: format
  
    Any value which is a valid key of the :attr:`smisk.serializers.extensions` dict.
  
    :type: string


  .. attribute:: serializer
  
    Serializer to use for encoding the response.
  
    The class attribute value serves as the application default serializer, used
    in cases where we need to encode the response, but the client is not specific
    about which serializer to use.
  
    If None, strict `TCN <http://www.ietf.org/rfc/rfc2295.txt>`__ applies.
  
    :see: :attr:`fallback_serializer`
    :type: :attr:`smisk.serialization.Serializer`

  
  .. attribute:: fallback_serializer
  
    Last-resort serializer, used for error responses and etc.
  
    If None when `Application.application_will_start` is called, this will
    be set to a HTML-serializer, and if none is available, simply the first
    registered serializer will be used.
  
    The class property is the only one used, the instance property has no 
    meaning and no effect, thus if you want to modify this during runtime,
    you should do this ``Response.fallback_serializer = my_serializer`` instead of
    this ``app.response.fallback_serializer = my_serializer``.
  
    :type: :attr:`smisk.serialization.Serializer`


  .. attribute:: charset
  
    Character encoding used to encode the response body.
  
    The value of ``Response.charset`` (class property value) serves as
    the application default charset.
  
    :type: string


  .. attribute:: charsets
  
    A list of acceptable charsets.
    
    The list have the form returned by :func:`~smisk.util.string.parse_qvalue_header()`
    (first item in the returned tuple) or is an empty list if any charset is acceptable.

    .. versionadded:: 1.1.6
  
    :type: list


  .. method:: send_file(path)
    
    Send a file to the client by using the host server sendfile-header
    technique.
    
    Automatically sets :samp:`Content-Type` header, using
    `mimetypes.guess_type <http://docs.python.org/library/mimetypes#mimetypes.guess_type>`_
    
    Calling this method implicitly commits the current HTTP transaction,
    sending the response immedately.
    
    :param  path: If this is a relative path, the host server defines the
                  behaviour.
    :type   path: string
    
    :raises EnvironmentError: If smisk does not know how to perform *sendfile*
                              through the current host server or if response has already started.
    :raises IOError:
  
  
  .. method:: adjust_status(has_content)

    .. versionadded:: 1.1.1
    
    Make sure appropriate status is set for the response.
  
  
  .. method:: remove_header(name)

    .. versionadded:: 1.1.1
    
    Remove any instance of header named or prefixed *name*.
  

  .. method:: remove_headers(*names)

    .. versionadded:: 1.1.1
    
    Remove any instance of headers named or prefixed *\*names*.
  
  
  .. method:: replace_header(header)

    .. versionadded:: 1.1.1
    
    Replace any instances of the same header type with *header*.
    
    >>> response.headers
    []
    >>> response.headers.append('Content-Type: text/humbug')
    >>> response.headers.append('X-Name: Fuffens')
    >>> response.headers
    ['Content-Type: text/humbug', 'X-Name: Fuffens']
    >>> response.replace_header('Content-type: text/plain')
    >>> response.headers
    ['X-Name: Fuffens', 'Content-type: text/plain']
  
  
  .. method:: accepts_charset(charset)

    .. versionadded:: 1.1.6
    
    Return True if *charset* is acceptable according to the :attr:`charsets` list.



.. ------------------------------------------------------------------------------------------



.. class:: Main(smisk.util.main.Main)


  .. attribute:: default_app_type

    Defaults to :class:`Application`


  .. method:: setup(application=None, appdir=None, *args, **kwargs)
  
    TODO


Modules
-------------------------------------------------

.. toctree::
  :maxdepth: 1
  
  smisk.mvc.console
  smisk.mvc.control
  smisk.mvc.decorators
  smisk.mvc.filters
  smisk.mvc.helpers
  smisk.mvc.http
  smisk.mvc.model
  smisk.mvc.routing
  smisk.mvc.template

