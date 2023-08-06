import unittest

class TestMarshal(unittest.TestCase):
    def _getFUT(self):
        from repoze.monty import marshal
        return marshal

    def test_empty_GET(self):
        f = self._getFUT()
        self.assertEqual(f({}, None), {})

    def _makeEnviron(self, kw=None):
        if kw is None:
            kw = {}
        env = {
            'wsgi.url_scheme': 'http',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '8080',
            'REQUEST_METHOD':'POST',
            'PATH_INFO': '/',
            'QUERY_STRING':'',
            }
        env.update(kw)
        return env

    def _makeMultipartEnviron(self, fields):
        ct, body = encode_multipart_formdata(fields)
        from StringIO import StringIO
        kw = dict(CONTENT_TYPE=ct, REQUEST_METHOD='POST')
        kw['wsgi.input'] = StringIO(body)
        environ = self._makeEnviron(kw)
        return environ

    def test_multipart_form_POST_noconvert(self):
        fields = [('login', 'login'),
                  ('password', 'password')]
        environ = self._makeMultipartEnviron(fields)
        f = self._getFUT()
        result = f(environ, environ['wsgi.input'])
        self.assertEqual(result['login'], u'login')
        self.assertEqual(result['password'], u'password')

    def test_multipart_form_POST_floatconvert_succeed(self):
        fields = [('myval:float', '1.0')]
        environ = self._makeMultipartEnviron(fields)
        f = self._getFUT()
        result = f(environ, environ['wsgi.input'])
        self.assertEqual(result['myval'], 1.0)
        
    def test_multipart_form_POST_floatconvert_fail(self):
        fields = [('myval:float', 'None')]
        environ = self._makeMultipartEnviron(fields)
        f = self._getFUT()
        self.assertRaises(ValueError, f, environ, environ['wsgi.input'])

    def test_multipart_form_POST_intconvert_succeed(self):
        fields = [('myval:int', '1')]
        environ = self._makeMultipartEnviron(fields)
        f = self._getFUT()
        result = f(environ, environ['wsgi.input'])
        self.assertEqual(result['myval'], 1)
        
    def test_multipart_form_POST_intconvert_fail(self):
        fields = [('myval:int', 'None')]
        environ = self._makeMultipartEnviron(fields)
        f = self._getFUT()
        self.assertRaises(ValueError, f, environ, environ['wsgi.input'])

    def test_multipart_form_POST_listconvert_succeed(self):
        fields = [('myval:list', '1'), ('myval:list', '2')]
        environ = self._makeMultipartEnviron(fields)
        f = self._getFUT()
        result = f(environ, environ['wsgi.input'])
        self.assertEqual(result['myval'], ['1', '2'])

    def test_multipart_form_POST_tupleconvert_succeed(self):
        fields = [('myval:tuple', '1'), ('myval:tuple', '2')]
        environ = self._makeMultipartEnviron(fields)
        f = self._getFUT()
        result = f(environ, environ['wsgi.input'])
        self.assertEqual(result['myval'], ('1', '2'))
        
    def test_multipart_form_POST_longconvert_succeed(self):
        import sys
        fields = [('myval:long', str(sys.maxint+1))]
        environ = self._makeMultipartEnviron(fields)
        f = self._getFUT()
        result = f(environ, environ['wsgi.input'])
        self.assertEqual(result['myval'], sys.maxint +1 )
        
    def test_multipart_form_POST_longconvert_fail(self):
        fields = [('myval:long', 'None')]
        environ = self._makeMultipartEnviron(fields)
        f = self._getFUT()
        self.assertRaises(ValueError, f, environ, environ['wsgi.input'])

    def test_multipart_form_POST_stringconvert_succeed(self):
        fields = [('myval:string', '1')]
        environ = self._makeMultipartEnviron(fields)
        f = self._getFUT()
        result = f(environ, environ['wsgi.input'])
        self.assertEqual(result['myval'], '1')

    def test_multipart_form_POST_requiredconvert_succeed(self):
        fields = [('myval:required', '1')]
        environ = self._makeMultipartEnviron(fields)
        f = self._getFUT()
        result = f(environ, environ['wsgi.input'])
        self.assertEqual(result['myval'], '1')

    def test_multipart_form_POST_requiredconvert_fail(self):
        fields = [('myval:required', '')]
        environ = self._makeMultipartEnviron(fields)
        f = self._getFUT()
        self.assertRaises(ValueError, f, environ, environ['wsgi.input'])

    def test_multipart_form_POST_tokensconvert_succeed(self):
        fields = [('myval:tokens', 'abc def')]
        environ = self._makeMultipartEnviron(fields)
        f = self._getFUT()
        result = f(environ, environ['wsgi.input'])
        self.assertEqual(result['myval'], ['abc', 'def'])

    def test_multipart_form_POST_linesconvert_succeed(self):
        fields = [('myval:tokens', 'abc\ndef')]
        environ = self._makeMultipartEnviron(fields)
        f = self._getFUT()
        result = f(environ, environ['wsgi.input'])
        self.assertEqual(result['myval'], ['abc', 'def'])

    def test_multipart_form_POST_textconvert_succeed(self):
        fields = [('myval:text', 'abc\r\ndef')]
        environ = self._makeMultipartEnviron(fields)
        f = self._getFUT()
        result = f(environ, environ['wsgi.input'])
        self.assertEqual(result['myval'], 'abc\ndef')

    def test_multipart_form_POST_boolconvert_succeed(self):
        fields = [('myval:boolean', '1')]
        environ = self._makeMultipartEnviron(fields)
        f = self._getFUT()
        result = f(environ, environ['wsgi.input'])
        self.assertEqual(result['myval'], True)

    def test_multipart_form_POST_multiconvert_succeed(self):
        fields = [('myval:list:int', '1'), ('myval:list:int', '2')]
        environ = self._makeMultipartEnviron(fields)
        f = self._getFUT()
        result = f(environ, environ['wsgi.input'])
        self.assertEqual(result['myval'], [1, 2])

    def test_multipart_form_POST_recordconvert_succeed(self):
        fields = [('person.fname:record', 'chris'), ('person.lname:record','m')]
        environ = self._makeMultipartEnviron(fields)
        f = self._getFUT()
        result = f(environ, environ['wsgi.input'])
        self.assertEqual(result['person']['fname'], u'chris')
        self.assertEqual(result['person']['lname'], u'm')

    def test_multipart_form_POST_recordsconvert_succeed(self):
        fields = [
            ('people.fname:records', 'chris'), ('people.lname:records','m'),
            ('people.fname:records', 'other'), ('people.lname:records','guy'),
            ]
        environ = self._makeMultipartEnviron(fields)
        f = self._getFUT()
        result = f(environ, environ['wsgi.input'])
        people = result['people']
        self.assertEqual(len(people), 2)
        chris = people[0]
        self.assertEqual(chris['fname'], u'chris')
        self.assertEqual(chris['lname'], u'm')
        other = people[1]
        self.assertEqual(other['fname'], u'other')
        self.assertEqual(other['lname'], u'guy')

    # needed tests: :ignore_empty, file upload tests

    # needed record tests: :default, :ignore_empty

    # what happened to ":date" in z3?

    # do we care about :action, :default_action?  what about :utext:utf8
    # and so on?

def encode_multipart_formdata(fields):
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

