# Set to your deployed proxy base URL (no trailing slash). See OneDrive_Streaming_Build_Guide / proxy-server/.
PROXY_URL = 'https://YOUR-APP.onrender.com'

import json
from urllib.request import urlopen, Request
from urllib.parse import urlencode


def get_files(share_url, subfolder=None, drive_id=None):
    params = {'url': share_url}
    if subfolder:
        params['subfolder'] = subfolder
    if drive_id:
        params['drive_id'] = drive_id
    req = Request(
        PROXY_URL + '/files?' + urlencode(params),
        headers={'User-Agent': 'KodiAddon/1.0'},
    )
    with urlopen(req, timeout=30) as r:
        body = json.loads(r.read().decode('utf-8'))
    return body.get('items') or []
