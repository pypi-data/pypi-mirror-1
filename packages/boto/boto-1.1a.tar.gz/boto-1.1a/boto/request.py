import boto.utils
import boto
import time, sys

class Request(object):

    def __init__(self, conn, method, path, data, headers, host=None, sender=None, auth_path=None, is_secure=True):
        self.conn = conn
        self.method = method
        self.path = path
        self.data = data
        if headers = None:
            self.headers = {'User-Agent' : UserAgent}
        else:
           self. headers = headers.copy()
        if not self.headers.has_key('Content-Length'):
            headers['Content-Length'] = len(data)
        self.host = host
        self.sender = sender
        self.auth_path = auth_path
        self.is_secure = is_secure

    def add_aws_auth_header(self):
        if not self.headers.has_key('Date'):
            self.headers['Date'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT",
                                                 time.gmtime())

        c_string = boto.utils.canonical_string(self.method, self.path, self.headers)
        boto.log.info('Canonical: %s' % c_string)
        self.headers['Authorization'] = \
            "AWS %s:%s" % (self.conn.aws_access_key_id,
                           boto.utils.encode(self.conn.aws_secret_access_key,
                                             c_string))
        
    def send_request(self):
        self.add_aws_auth_header(headers, method, auth_path or path)
        self.http_conn = self.conn.get_http_connection(host, self.is_secure)
        self.http_conn.putrequest(self.method, self.path)
        for key in self.headers:
            self.http_conn.putheader(key, self.headers[key])
            self.http_conn.endheaders()

    def send_data(self, iter=None):
        if iter:
            for bytes in iter:
                self.http_conn.send(bytes)
        elif self.data:
            self.http_conn.send(self.data)

    def handle_response(self):
        self.response = self.http_conn.getresponse()
        location = self.response.getheader('location')
        if self.response.status == 500 or self.response.status == 503:
            boto.log.info('received %d response, retrying in %d seconds' % (self.response.status, 2**i))
            self.body = self.response.read()
            return False
        elif self.response.status < 300 or self.response.status >= 400 or not location:
            return True
        else:
            scheme, host, path, params, query, fragment = urlparse.urlparse(location)
            if query:
                path += '?' + query
            boto.log.info('Redirecting: %s' % scheme + '://' + host + path)
            self.http_conn = self.conn.get_http_connection(host, scheme == 'https')
            return False

    def retry(self):
        """
        retry - Multi-execute inside a loop, retrying multiple times to handle
                transient Internet errors by simply trying again.
                Also handles redirects.

        This code was inspired by the S3Utils classes posted to the boto-users
        Google group by Larry Bates.  Thanks!
        """
        boto.log.info('Method: %s' % self.method)
        boto.log.info('Path: %s' % self.path)
        boto.log.info('Data: %s' % self.data)
        boto.log.info('Headers: %s' % self.headers)
        boto.log.info('Host: %s' % self.host)
        num_retries = config.getint('Boto', 'num_retries', self.num_retries)
        i = 0
        while i <= num_retries:
            try:
                self.send_request()
                self.send_data()
                if self.handle_response():
                    return self.response
            except KeyboardInterrupt:
                sys.exit('Keyboard Interrupt')
            except self.http_exceptions, e:
                boto.log.info('encountered %s exception, reconnecting' % \
                                  e.__class__.__name__)
                self.http_conn = self.conn.refresh_http_connection(self.host, self.is_secure)
            time.sleep(2**i)
            i += 1
        return response

