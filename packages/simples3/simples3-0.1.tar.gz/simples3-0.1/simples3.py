r"""A Simple Amazon AWS S3 interface

And it really is simple.

Setup::

    >>> s = S3Bucket("mybucket", 
    ...              access_key="ACESSS KEY",
    ...              secret_key="SECRET KEY")
    ... 
    >>> print s  # doctest: +ELLIPSIS
    <S3Bucket ... at 'https://s3.amazonaws.com/...'>

or if you'd like to use virtual host S3::

    >>> s = S3Bucket("mybucket",
    ...              access_key="ACCESS KEY",
    ...              secret_key="SECRET KEY",
    ...              base_url="http://yo.se")
    >>> print s  # doctest: +ELLIPSIS
    <S3Bucket ... at 'http...'>

Note that missing slash above, it's important. Think of it as
"The prefix to which all calls are made." Also the scheme can be `https` or
regular `http`, or any other urllib2-compatible scheme (that is: you can
register your own.)

Now, let's start doing something useful. Start out by putting a simple file
onto there::

    >>> s.put("my file", "my content")

Alright, and fetch it back::

    >>> f = s.get("my file")
    >>> f.read()
    'my content'

Nice and tidy, but what if we want to know more about our fetched file? Easy::

    >>> f.s3_info["modify"]  # doctest: +ELLIPSIS
    datetime.datetime(...)
    >>> f.s3_info["mimetype"]
    'application/octet-stream'
    >>> f.s3_info.keys()
    ['mimetype', 'modify', 'headers', 'date', 'size', 'metadata']
    >>> f.close()

Note that the type was octet stream. That's simply because we didn't specify
anything else. Do that using the `mimetype` keyword argument::

    >>> s.put("my new file!", "Improved content!\nMultiple lines!",
    ...       mimetype="text/plain")

Let's be cool and use the very Pythonic API to do fetch::

    >>> f = s["my new file!"]
    >>> print f.read()
    Improved content!
    Multiple lines!
    >>> f.s3_info["mimetype"]
    'text/plain'
    >>> f.close()

Great job, huh. Now, let's delete it::

    >>> del s["my new file!"]

Could've used the `delete` method instead, but we didn't.

If you just want to know about a key, ask and ye shall receive::

    >>> from pprint import pprint
    >>> s["This is a testfile."] = S3File("Hi!", metadata={"hairdo": "Secret"})
    >>> pprint(s.info("test"))  # doctest: +ELLIPSIS
    {'date': datetime.datetime(...),
     'headers': {'content-length': '3',
                 'content-type': 'application/x-octet-stream',
                 'date': '...',
                 'etag': '"..."',
                 'last-modified': '...',
                 'server': 'AmazonS3',
                 'x-amz-id-2': '...',
                 'x-amz-meta-hairdo': 'Secret',
                 'x-amz-request-id': '...'},
     'metadata': {'hairdo': 'Secret'},
     'mimetype': 'application/x-octet-stream',
     'modify': datetime.datetime(...),
     'size': 3}

Notable is that you got the metadata parsed out in the `metadata` key. You
might also have noticed how the file was uploaded, using an `S3File` object
like that. That's a nicer way to do it, in a way.

The `S3File` simply takes its keyword arguments, and passes them on to `put`
later. Other than that, it's a str subclass.

And the last dict-like behavior is in tests::

    >>> "This is a testfile." in s
    True
    >>> del s["This is a testfile."]
    >>> "This is a testfile." in s
    False

You can also set a canned ACL using `put`, which is too simple::

    >>> s.put("test/foo", "test", acl="public-read")
    >>> s.put("test/bar", "rawr", acl="public-read")

Boom. What's more? Listing the bucket::

    >>> for (key, modify, etag, size) in s.listdir(prefix="test/"):
    ...     print "%r (%r) is size %r, modified %r" % (key, etag, size, modify)
    ... # doctest: +ELLIPSIS
    'test/bar' ('"..."') is size 4, modified datetime.datetime(...)
    'test/foo' ('"..."') is size 4, modified datetime.datetime(...)

That about sums it up.
"""

import time
import hmac
import hashlib
import re
import urllib
import urllib2
import datetime
import mimetypes

rfc822_fmt = '%a, %d %b %Y %H:%M:%S GMT'
iso8601_fmt = '%Y-%m-%dT%H:%M:%S.000Z'

def _amz_canonicalize(headers):
    r"""Canonicalize AMZ headers in that certain AWS way.

    >>> _amz_canonicalize({"x-amz-test": "test"})
    'x-amz-test:test\n'
    >>> _amz_canonicalize({})
    ''
    """
    rv = {}
    for header, value in headers.iteritems():
        header = header.lower()
        if header.startswith("x-amz-"):
            rv.setdefault(header, []).append(value)
    return "".join(":".join((h, ",".join(v))) + "\n" for h, v in rv.iteritems())

def metadata_headers(metadata):
    return dict(("X-AMZ-Meta-" + h, v) for h, v in metadata.iteritems())

def headers_metadata(headers):
    return dict((h[11:], v) for h, v in headers.iteritems()
                            if h.lower().startswith("x-amz-meta-"))

def _rfc822_dt(v): return datetime.datetime.strptime(v, rfc822_fmt)
def _iso8601_dt(v): return datetime.datetime.strptime(v, iso8601_fmt)

def aws_md5(data):
    """Make an AWS-style MD5 hash (digest in base64).

    >>> aws_md5("Hello!")
    'lS0sVtBIWVgzZ0e83ZhZDQ=='
    """
    return hashlib.md5(data).digest().encode("base64")[:-1]

def aws_urlquote(value):
    r"""AWS-style quote a URL part.

    >>> aws_urlquote("/bucket/a key")
    '/bucket/a%20key'
    >>> aws_urlquote(u"/bucket/\xe5der")
    '/bucket/%C3%A5der'
    """
    if isinstance(value, unicode):
        value = value.encode("utf-8")
    return urllib.quote(value, "/")

def guess_mimetype(fn, default="application/octet-stream"):
    """Guess a mimetype from filename *fn."""
    if "." not in fn:
        return default
    extension = fn.rsplit(".", 1)[1].lower()
    if extension == "jpg": extension = "jpeg"
    return mimetypes.guess_type("." + extension)[0] or default

def info_dict(headers):
   return {"size": int(headers["content-length"]),
           "mimetype": headers.get("content-type"),
           "date": _rfc822_dt(headers["date"]),
           "modify": _rfc822_dt(headers["last-modified"]),
           "headers": headers,
           "metadata": headers_metadata(headers)}

def name(o):
    """Find the name of *o*.

    Functions:
    >>> name(name)
    'name'
    >>> def my_fun(): pass
    >>> name(my_fun)
    'my_fun'

    Classes:
    >>> name(Exception)
    'Exception'
    >>> class MyKlass(object): pass
    >>> name(MyKlass)
    'MyKlass'

    Instances:
    >>> name(Exception()), name(MyKlass())
    ('Exception', 'MyKlass')

    Types:
    >>> name(str), name(object), name(int)
    ('str', 'object', 'int')

    Type instances:
    >>> name("Hello"), name(True), name(None), name(Ellipsis)
    ('str', 'bool', 'NoneType', 'ellipsis')
    """
    if hasattr(o, "__name__"): return o.__name__
    for o in getattr(o, "__mro__", o.__class__.__mro__):
        return name(o)

class S3Error(Exception):
    def __init__(self, message, **kwds):
        self.message = message
        self.extra = kwds.copy()

    def __str__(self):
        rv = self.message
        if self.extra:
            key_it = iter(self.extra)
            rv += " ("
            prep = ""
            while len(rv) < 79:
                try:
                    key = key_it.next()
                except StopIteration:
                    break
                rv += prep + key + "=" + repr(self.extra[key])
                prep = ", "
            rv += ")"
        return rv

    @classmethod
    def from_urllib(cls, e):
        """Try to read the real error from AWS."""
        self = cls("HTTP error", code=e.code, url=e.filename)
        self.code = e.code
        self.fp = fp = e.fp
        # The latter part of this clause is to avoid some weird bug in urllib2
        # and AWS which has it read as if chunked, and AWS gives empty reply.
        if fp and dict(fp.info()).get("Content-Length", 0):
            self.data = data = fp.read()
            begin, end = data.find("<Message>"), data.find("</Message>")
            if min(begin, end) >= 0:
                self.full_message = msg = data[begin + 9:end]
                self.message = msg[:50]
                if self.message != msg:
                    self.message += "..."
        return self

class StreamHTTPHandler(urllib2.HTTPHandler):
    pass

class StreamHTTPSHandler(urllib2.HTTPSHandler):
    pass

class AnyMethodRequest(urllib2.Request):
    def __init__(self, method, *args, **kwds):
        self.method = method
        urllib2.Request.__init__(self, *args, **kwds)

    def get_method(self):
        return self.method

class S3File(str):
    def __new__(cls, value, **kwds):
        return super(S3File, cls).__new__(cls, value)

    def __init__(self, value, **kwds):
        kwds["data"] = value
        self.kwds = kwds

    def put_into(self, bucket, key):
        return bucket.put(key, **self.kwds)

class S3Bucket(object):
    amazon_s3_base = "https://s3.amazonaws.com/"
    listdir_re = re.compile(r"^<Key>(.+?)</Key>"
                            r"<LastModified>(.{24})</LastModified>"
                            r"<ETag>(.+?)</ETag><Size>(\d+?)</Size>$")

    def __init__(self, name, access_key=None, secret_key=None, base_url=None):
        self.opener = urllib2.build_opener(StreamHTTPHandler, StreamHTTPSHandler)
        self.name = name
        self.access_key = access_key
        self.secret_key = secret_key
        if not base_url:
            self.base_url = self.amazon_s3_base + aws_urlquote(name)
        else:
            self.base_url = base_url

    def __str__(self):
        return "<%s %s at %r>" % (self.__class__.__name__, self.name, self.base_url)

    def __repr__(self):
        return self.__class__.__name__ + "(%r, access_key=%r, base_url=%r)" % (
            self.name, self.access_key, self.base_url)

    def __getitem__(self, name): return self.get(name)
    def __delitem__(self, name): return self.delete(name)
    def __setitem__(self, name, value):
        if hasattr(value, "put_into"):
            return value.put_into(self, name)
        else:
            return self.put(name, value)
    def __contains__(self, name):
        try:
            self.info(name)
        except KeyError:
            return False
        else:
            return True

    def sign_description(self, desc):
        """AWS-style sign data."""
        hasher = hmac.new(self.secret_key, desc.encode("utf-8"), hashlib.sha1)
        return hasher.digest().encode("base64")[:-1]

    def make_description(self, method, key=None, data=None,
                         headers={}, subresource=None, bucket=None):
        # The signature descriptor is detalied in the developer's PDF on p. 65.
        # Calculate canonicalized resource.
        res = "/"
        if bucket or bucket is None:
            res += aws_urlquote(bucket or self.name)
        res += "/"
        if key:
            res += aws_urlquote(key)
        if subresource:
            res += "?" + subresource
        # Make description. :/
        return "\n".join((method, headers.get("Content-MD5", ""),
            headers.get("Content-Type", ""), headers.get("Date", ""))) + "\n" +\
            _amz_canonicalize(headers) + res

    def get_request_signature(self, method, key=None, data=None,
                              headers={}, subresource=None, bucket=None):
        return self.sign_description(self.make_description(method, key=key,
            data=data, headers=headers, subresource=subresource, bucket=bucket))

    def new_request(self, method, key=None, args=None, data=None, headers={}):
        url = self.base_url + "/"
        headers = headers.copy()
        if key:
            url += aws_urlquote(key)
        if args:
            if hasattr(args, "iteritems"):
                args_items = args.iteritems()
            elif hasattr(args, "items"):
                args_items = args.items()
            else:
                args_items = args
            url += "?" + ";".join("=".join(map(urllib.quote_plus, item))
                                  for item in args_items)
        if data and "Content-MD5" not in headers:
            headers["Content-MD5"] = aws_md5(data)
        if "Date" not in headers:
            headers["Date"] = time.strftime(rfc822_fmt, time.gmtime())
        if "Authorization" not in headers:
            sign = self.get_request_signature(method, key=key, data=data,
                                              headers=headers)
            headers["Authorization"] = "AWS %s:%s" % (self.access_key, sign)
        return AnyMethodRequest(method, url, data=data, headers=headers)

    def open_request(self, request, errors=True):
            return self.opener.open(request)

    def make_request(self, method, key=None, args=None, data=None, headers={}):
        for retry_no in xrange(10):
            request = self.new_request(method, key=key, args=args,
                                       data=data, headers=headers)
            try:
                return self.open_request(request)
            except urllib2.HTTPError, e:
                raise S3Error.from_urllib(e)
        else:
            raise RuntimeError("ran out of retries")  # Shouldn't happen.

    def get(self, key):
        response = self.make_request("GET", key=key)
        response.s3_info = info_dict(dict(response.info()))
        return response

    def info(self, key):
        try:
            response = self.make_request("HEAD", key=key)
        except S3Error, e:
            if e.code == 404:
                raise KeyError(key)
            raise e
        rv = info_dict(dict(response.info()))
        response.close()
        return rv

    def put(self, key, data=None, acl=None, metadata={}, mimetype=None):
        headers = {"Content-Type": mimetype or guess_mimetype(key)}
        headers.update(metadata_headers(metadata))
        headers.update({"Content-Length": str(len(data)),
                        "Content-MD5": aws_md5(data)})
        if acl:
            headers["X-AMZ-ACL"] = acl
        self.make_request("PUT", key=key, data=data, headers=headers).close()

    def delete(self, key):
        try:
            resp = self.make_request("DELETE", key=key)
            resp.close()
        # Python 2.5: urllib2 raises an exception for 204.
        except S3Error, e:
            if e.code == 204:
                return True
            elif e.code == 404:
                raise KeyError(key)
            raise
        # Python 2.6: urllib2 does the right thing for 204.
        else:
            if resp.code != 204:
                raise KeyError(key)
    
    def listdir(self, prefix=None, marker=None, limit=None, delimiter=None):
        """List contents of bucket.

        *prefix*, if given, predicats `key.startswith(prefix)`.
        *marker*, if given, predicates `key > marker`, lexicographically.
        *limit*, if given, predicates `len(keys) <= limit`.
        """
        mapping = (("prefix", prefix),
                   ("marker", marker),
                   ("max-keys", limit),
                   ("delimiter", delimiter))
        args = dict((k, v) for (k, v) in mapping if v is not None)
        response = self.make_request("GET", args=args)
        buffer = ""
        while True:
            data = response.read(4096)
            buffer += data
            while True:
                pos_end = buffer.find("</Contents>")
                if pos_end == -1:
                    break
                piece = buffer[buffer.index("<Contents>") + 10:pos_end]
                buffer = buffer[pos_end + 10:]
                info = piece[:piece.index("<Owner>")]
                mo = self.listdir_re.match(info)
                if not mo:
                    raise ValueError("unexpected: %r" % (piece,))
                key, modify, etag, size = mo.groups()
                # FIXME A little brittle I would say...
                etag = etag.replace("&quot;", '"')
                yield key, _iso8601_dt(modify), etag, int(size)
            if not data:
                break

if __name__ == "__main__":
    import doctest
    doctest.testmod()
