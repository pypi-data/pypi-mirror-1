  @classmethod
  def find_function(cls, f):
    '''Find the closest callable function containing func_code.
    
    :returns: (function closest parent to f with func_code, function with func_code) 
              or `None2` if not found
    :rtype:   tuple
    '''
    fc = f
    if isinstance(f, FunctionType):
      # This might work, for instance for ensure_va_kwa wrapper
      try:
        f = f.im_func
        fc = f
      except AttributeError:
        pass
    elif isinstance(f, MethodType):
      try:
        fc = f.im_func
      except AttributeError:
        return None2
    elif isinstance(f, (TypeType, ClassType, InstanceType, ObjectType)):
      try:
        f = f.__call__
        fc = f.im_func
      except AttributeError:
        return None2
    try:
      fc.func_code
      return (f, fc)
    except AttributeError:
      print cls.format_members(f)
      return None2


# unittest snippet
  def test_1_find_function(self):
    a = A()
    b = B()
    def plain(self):
      pass
    assert introspect.find_function(plain) == (plain, plain)
    assert introspect.find_function(a) == (a.__call__, a.__call__.im_func)
    assert introspect.find_function(A) == (A.__call__, A.__call__.im_func)
    assert introspect.find_function(A.hello) == (A.hello, A.hello.im_func)
    assert introspect.find_function(a.hello) == (a.hello, a.hello.im_func)
    assert introspect.find_function(A.ping) == (A.ping, A.ping.im_func)
    assert introspect.find_function(a.ping) == (a.ping, a.ping.im_func)
    assert introspect.find_function(b) == None2
    assert introspect.find_function(B) == None2