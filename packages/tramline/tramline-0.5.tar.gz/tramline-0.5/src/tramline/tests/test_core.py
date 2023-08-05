import os, shutil
import unittest
from StringIO import StringIO

from tramline.core import inputfilter, outputfilter, tramline_upload_path,\
     tramline_repository_path, parse_header, create_paths, tramline_path

tramline_path = '/tmp/'

class Request:
    def __init__(self, method):
        self.headers_in = { 'Content-Type' : 'multipart/form-data' }
        self.headers_out = {}
        self.main = None
        self.method = method

    def get_options(self):
        return {'tramline_path': tramline_path}
        
class Filter:
    def __init__(self, input, output, is_last=True, method='POST'):
        self.input = input
        self.output = output
        self.is_closed = False
        self.req = Request(method)
        self.is_last = is_last
        
    def read(self, length=None):
        data = self.input.read()
        if data == '' and self.is_last:
            return None
        return data
        
    def readline(self, length=None):
        data = self.input.readline()
        if data == '' and self.is_last:
            return None
        return data
    
    def write(self, data):
        self.output.write(data)
        
    def close(self):
        self.is_closed = True

    def disable(self):
        pass

    def pass_on(self):
        data = self.input.read()
        self.output.write(data)

    def flush(self):
        pass
    
class TramlineTests(unittest.TestCase):

    def setUp(self):
        pass
# XXX is cleaning up the right way to go? it's hard to debug test failures
# then and previous real uploads are gone..
#        shutil.rmtree(tramline_path, ignore_errors=True)
#        create_paths()
        
    def tearDown(self):
        pass
#        shutil.rmtree(tramline_path, ignore_errors=True)
    
    def test_inputfilter(self):
        input = open(get_data_path('input1.txt'), 'rb')
        output = StringIO()
        filter = Filter(input, output)
        
        inputfilter(filter)

        input.close()

        f = open(get_data_path('input1.txt'), 'rb')
        data = f.read()
        f.close()

        output_data = output.getvalue()
        self.assertEquals(data, output_data)
        self.assert_(filter.is_closed)

        self.assert_('tramline' not in filter.req.headers_in)
        
    def test_inputfilter_file(self):
        input = open(get_data_path('input2.txt'), 'rb')
        output = StringIO()
        filter = Filter(input, output)
        
        inputfilter(filter)

        input.close()

        output_data = output.getvalue()

        file_id = self.file_id(output_data)
        f = open(os.path.join(tramline_upload_path(filter.req), file_id), 'rb')
        data = f.read()
        f.close()
        self.assertEquals(
            'first line\nsecond line\n', data)
        self.assert_('tramline' in filter.req.headers_in)
        
    def test_inputfilter_file2(self):
        input = open(get_data_path('input4.txt'), 'rb')
        output = StringIO()
        filter = Filter(input, output)
        
        inputfilter(filter)

        input.close()

        output_data = output.getvalue()

        file_id = self.file_id(output_data)
        f = open(os.path.join(tramline_upload_path(filter.req), file_id), 'rb')
        
        data = f.read()
        f.close()
        self.assertEquals(
            'first line\nsecond line', data)
        
    def test_split_filter(self):
        f = open(get_data_path('input2.txt'), 'rb')
        data = f.read()
        f.close()
        halfway = len(data) / 2
        first_half = data[:halfway]
        second_half = data[halfway:]

        output = StringIO()
        
        filter = Filter(StringIO(first_half), output, is_last=False)
        inputfilter(filter)
        filter.input = StringIO(second_half)
        filter.is_last = True
        inputfilter(filter)
        
        output_data = output.getvalue()

        file_id = self.file_id(output_data)
        f = open(os.path.join(tramline_upload_path(filter.req), file_id), 'rb')

        data = f.read()
        f.close()
        self.assertEquals(
            'first line\nsecond line\n', data)

    def test_three_split_filter(self):
        f = open(get_data_path('input2.txt'), 'rb')
        data = f.read()
        f.close()

        third = len(data) / 3
        first = data[:third]
        second = data[third:third + third]
        third = data[third + third:]
        
        output = StringIO()
        
        filter = Filter(StringIO(first), output, is_last=False)
        inputfilter(filter)
        filter.input = StringIO(second)
        inputfilter(filter)
        filter.input = StringIO(third)
        filter.is_last = True
        inputfilter(filter)
        
        output_data = output.getvalue()

        file_id = self.file_id(output_data)
        f = open(os.path.join(tramline_upload_path(filter.req), file_id), 'rb')
        data = f.read()
        f.close()
        self.assertEquals(
            'first line\nsecond line\n', data)

    def test_empty_file(self):
        input = open(get_data_path('input5.txt'), 'rb')
        output = StringIO()
        filter = Filter(input, output)

        inputfilter(filter)

        input.close()

        output_data = output.getvalue()

        file_id = self.file_id(output_data)
        self.assertEquals('', file_id)
        
    def test_abort(self):
        input = open(get_data_path('input2.txt'), 'rb')
        output = StringIO()
        filter = Filter(input, output)

        inputfilter(filter)
        input.close()

        output_data = output.getvalue()

        file_id = self.file_id(output_data)

        tramline_id = filter.req.headers_in['tramline_id']
        
        # now send 'foo' back to the client in the response
        output = StringIO()
        filter = Filter(StringIO('foo'), output)
        filter.req.headers_in['tramline_id'] = tramline_id
        # don't send 'tramline_ok'
        
        # now send output
        outputfilter(filter)

        # we should get 'foo'
        self.assertEquals('foo', output.getvalue())
        
        # file should be gone
        self.assert_(not os.path.exists(os.path.join(
            tramline_upload_path(filter.req), file_id)))
        # and not be stored
        self.assert_(not os.path.exists(os.path.join(
            tramline_repository_path(filter.req), file_id)))

    def test_commit(self):
        input = open(get_data_path('input2.txt'), 'rb')
        output = StringIO()
        filter = Filter(input, output)

        inputfilter(filter)
        input.close()

        output_data = output.getvalue()

        file_id = self.file_id(output_data)

        tramline_id = filter.req.headers_in['tramline_id']
        
        # now send 'foo' back to the client in the response
        output = StringIO()
        filter = Filter(StringIO('foo'), output)
        filter.req.headers_in['tramline_id'] = tramline_id
        # send tramline_ok
        filter.req.headers_out['tramline_ok'] = 'something'

        # now send output
        outputfilter(filter)

        # we should get 'foo'
        self.assertEquals('foo', output.getvalue())
        
        # file should be gone in upload
        self.assert_(not os.path.exists(os.path.join(
            tramline_upload_path(filter.req), file_id)))
        # and should be stored
        self.assert_(os.path.exists(os.path.join(
            tramline_repository_path(filter.req), file_id)))

    def test_get_output(self):
        # send 'foo' back to the client
        output = StringIO()
        filter = Filter(StringIO('foo'), output, method='GET')
        # set no special tramline headers
        # now send output
        outputfilter(filter)
        # we should get 'foo'
        self.assertEquals('foo', output.getvalue())

    def test_file_serve(self):
        # first upload file and commit
        input = open(get_data_path('input2.txt'), 'rb')
        output = StringIO()
        filter = Filter(input, output)

        inputfilter(filter)
        input.close()

        output_data = output.getvalue()

        file_id = self.file_id(output_data)

        tramline_id = filter.req.headers_in['tramline_id']
        
        # now send 'foo' back to the client in the response
        output = StringIO()
        filter = Filter(StringIO('foo'), output)
        filter.req.headers_in['tramline_id'] = tramline_id
        # send tramline_ok
        filter.req.headers_out['tramline_ok'] = 'something'

        # now send output
        outputfilter(filter)

        # now send file as output
        
        output = StringIO()
        # send file_id in response body
        filter = Filter(StringIO(file_id), output, method='GET')
        # set tramline_file header to notify tramline to take action
        filter.req.headers_out['tramline_file'] = None
        # now send
        outputfilter(filter)
        # output should now contain file
        f = open(os.path.join(
            tramline_repository_path(filter.req), file_id), 'rb')
        expected_data = f.read()
        f.close()
        data = output.getvalue()
        self.assertEquals(expected_data, data)
        
    def test_parse_header(self):
        name, d = parse_header('form-data; name="test"')
        self.assertEquals('form-data',
                          name)
        self.assertEquals('test',
                          d['name'])
        
    def test_parse_header_nothing(self):
        name, d = parse_header('form-data')
        self.assertEquals('form-data',
                          name)
        self.assertEquals(0, len(d))

    def test_parse_header_multiple(self):
        name, d = parse_header('form-data; name="test"; filename="foo"')
        self.assertEquals('form-data',
                          name)
        self.assertEquals(2, len(d))
        self.assertEquals('test',
                          d['name'])
        self.assertEquals('foo',
                          d['filename'])

    def test_parse_header_whitespace(self):
        name, d = parse_header('form-data;  name="test";filename="foo" ')
        self.assertEquals('form-data',
                          name)
        self.assertEquals(2, len(d))
        self.assertEquals('test',
                          d['name'])
        self.assertEquals('foo',
                          d['filename'])

    def test_parse_header_noquotes(self):
        name, d = parse_header('form-data; name=test;filename=foo')
        self.assertEquals('form-data',
                          name)
        self.assertEquals(2, len(d))
        self.assertEquals('test',
                          d['name'])
        self.assertEquals('foo',
                          d['filename'])

    def file_id(self, data, start=0):
        i = data.find('filename', start)
        if i == -1:
            return None
        i = data.find('\r\n\r\n', i) + 4
        j = data.find('\r\n', i)
        id = data[i:j].strip()
        return id
    
def get_data_path(name):
    path, rest = os.path.split(__file__)
    return os.path.join(path, 'data', name)
    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TramlineTests))
    return suite
