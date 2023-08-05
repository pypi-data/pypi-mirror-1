#!/usr/bin/python

"""
REST client convenience library

This module contains everything that's needed for a nice REST client.

the main function it provides is rest_invoke(), which will make an HTTP
request to a REST server. it allows for all kinds of nice things like:

    * alternative verbs: POST, PUT, DELETE, etc.
    * parameters
    * file uploads (multipart/form-data)
    * proper unicode handling
    * Accept: headers
    * ability to specify other headers

this library is mostly a wrapper around the standard urllib and
httplib functionality, but also includes file upload support via a
python cookbook recipe
(http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146306) and
has had additional work to make sure high unicode characters in the
url, parameters, or headers don't cause any UnicodeEncodeError problems. 


CHANGESET:

  * 2006-02-22 - Anders - handles ints in params + headers correctly now

"""


import urllib2,urllib
import httplib, mimetypes
import types

def post_multipart(host, selector, fields, files, headers={}):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    content_type, body = encode_multipart_formdata(fields, files)
    h = httplib.HTTP(host.encode('utf8'))
    h.putrequest('POST', selector.encode('utf8'))

    for k in headers.keys():
        if k.lower() != "content-type":
            h.putheader(k,headers[k])
    h.putheader('host',host.encode('utf8'))
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.endheaders()
    h.send(body)
    errcode, errmsg, headers = h.getreply()
    return h.file.read()

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(str(value))
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(str(value))
    L.append('--' + BOUNDARY + '--')
    L.append('')
    L = [str(l) for l in L]

    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


def rest_invoke(url,method=u"GET",params={},files={},accept=[],headers={}):
    """ make an HTTP request with all the trimmings.

    rest_invoke() will make an HTTP request and can handle all the
    advanced things that are necessary for a proper REST client to handle:

    * alternative verbs: POST, PUT, DELETE, etc.
    * parameters
    * file uploads (multipart/form-data)
    * proper unicode handling
    * Accept: headers
    * ability to specify other headers

    rest_invoke() returns the body of the response that it gets from
    the server.

    rest_invoke() does not try to do any fancy error handling. if the
    server is down or gives an error, it will propagate up to the
    caller.

    this function expects to receive unicode strings. passing in byte
    strings risks double encoding.

    paramaters:

    url: the full url you are making the request to
    method: HTTP verb to use. defaults to GET
    params: dictionary of params to include in the request
    files: dictionary of files to upload. the structure is

          param : {'file' : file object, 'filename' : filename}

    accept: list of mimetypes to accept in order of preference. defaults to '*/*'
    headers: dictionary of additional headers to send to the server
    
    """
    
    
    (scheme,host,path,ps,query,fragment) = urllib2.urlparse.urlparse(url)
    for k in params.keys():
        if type(k) not in types.StringTypes:
            new_k = str(k)
            params[new_k] = params[k]
            del params[k]
        if type(params[k]) not in types.StringTypes:
            params[k] = str(params[k])
        try:
            v = params[k].encode('ascii')                
            k = k.encode('ascii')
        except UnicodeEncodeError:
            new_k = k.encode('utf8')
            new_v = params[k].encode('utf8')
            params[new_k] = new_v
            del params[k]
    for k in headers.keys():
        if type(k) not in types.StringTypes:
            new_k = str(k)
            headers[new_k] = headers[k]
            del headers[k]
        if type(headers[k]) not in types.StringTypes:
            headers[k] = str(headers[k])        
        try:
            v = headers[k].encode('ascii')                
            k = k.encode('ascii')
        except UnicodeEncodeError:
            new_k = k.encode('utf8')
            new_v = headers[k].encode('utf8')
            headers[new_k] = new_v
            del headers[k]
    # fix keys in files
    for k in files.keys():
        if type(k) not in types.StringTypes:
            new_k = str(k)
            params[new_k] = params[k]
            del params[k]
        if type(params[k]) not in types.StringTypes:
            params[k] = str(params[k])
        try:
            k = k.encode('ascii')
        except UnicodeEncodeError:
            new_k = k.encode('utf8')
            files[new_k] = files[k]
            del files[k]                
    # second pass to fix filenames
    for k in files.keys():
        try:
            f = files[k]['filename'].encode('ascii')
        except UnicodeEncodeError:
            files[k]['filename'] = files[k]['filename'].encode('utf8')

    if ps:
        path += ";" + ps
    if query:
        path += "?" + query

    if accept:
        headers['Accept'] = ','.join(accept)
    else:
        headers['Accept'] = '*/*'
        
    if files:
        return post_multipart(host,path,[(k,params[k]) for k in params.keys()],
                              [(k,files[k]['filename'],files[k]['file']) for k in files.keys()],
                              headers)
    else:

        params = urllib.urlencode(params)
        conn = httplib.HTTPConnection(host.encode('utf8'))
        conn.request(method.encode('utf8'), path.encode('utf8'), params,headers)
        response = conn.getresponse()
        r = response.read()
        conn.close()
        return r


if __name__ == "__main__":
    print rest_invoke("http://localhost:9090/",
                      method="POST",params={'value' : 'store this'},accept=["text/plain","text/html"])
    image = open('sample.jpg').read()
    r = rest_invoke("http://resizer.ccnmtl.columbia.edu/resize",method="POST",files={'image' : {'file' : image, 'filename' : 'sample.jpg'}})
    out = open("thumb.jpg","w")
    out.write(r)
    out.close()
    # evil unicode tests
    print rest_invoke(u"http://localhost:9090/foo\u2012/",params={u'foo\u2012' : u'\u2012'},
                      headers={u"foo\u2012" : u"foo\u2012"})
    
    r = rest_invoke(u"http://localhost:9090/resize\u2012",method="POST",files={u'image\u2012' : {'file' : image, 'filename' : u'samp\u2012le.jpg'}})    
