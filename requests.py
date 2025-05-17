import urllib.request
import urllib.error

class Response:
    def __init__(self, url, data=b"", headers=None, status=200):
        self.url = url
        self.content = data
        self.text = data.decode('utf-8', 'replace') if isinstance(data, bytes) else data
        self.headers = headers or {}
        self.status_code = status

def _request(method, url, headers=None, timeout=10):
    req = urllib.request.Request(url, headers=headers or {}, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
        return Response(url, data, dict(resp.headers), resp.status)

def get(url, headers=None, timeout=10):
    return _request('GET', url, headers, timeout)

def head(url, headers=None, allow_redirects=True, timeout=10):
    try:
        return _request('HEAD', url, headers, timeout)
    except urllib.error.HTTPError as e:
        return Response(url, b"", dict(e.headers), e.code)

