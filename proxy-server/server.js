const express = require('express');
const fetch = require('node-fetch');
const app = express();
const PORT = process.env.PORT || 3000;

const TENANT = process.env.TENANT_ID;
const CLIENT = process.env.CLIENT_ID;
const SECRET = process.env.CLIENT_SECRET;

let tokenCache = { token: null, expires: 0 };

async function getToken() {
  if (tokenCache.token && Date.now() < tokenCache.expires - 60000) {
    return tokenCache.token;
  }
  const res = await fetch(
    `https://login.microsoftonline.com/${TENANT}/oauth2/v2.0/token`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'client_credentials',
        client_id: CLIENT,
        client_secret: SECRET,
        scope: 'https://graph.microsoft.com/.default'
      })
    }
  );
  const data = await res.json();
  if (!data.access_token) {
    throw new Error('Token fetch failed: ' + JSON.stringify(data));
  }
  tokenCache = {
    token: data.access_token,
    expires: Date.now() + data.expires_in * 1000
  };
  return tokenCache.token;
}

function encodeShare(url) {
  const b64 = Buffer.from(url).toString('base64');
  return 'u!' + b64.replace(/=/g, '').replace(/\//g, '_').replace(/\+/g, '-');
}

app.get('/files', async (req, res) => {
  try {
    const shareUrl = req.query.url;
    const subfolder = req.query.subfolder;
    const driveId = req.query.drive_id;
    const token = await getToken();
    let graphUrl;
    if (subfolder && driveId) {
      graphUrl = `https://graph.microsoft.com/v1.0/drives/${driveId}/items/${subfolder}/children?$top=500`;
    } else {
      const tokenId = encodeShare(shareUrl);
      graphUrl = `https://graph.microsoft.com/v1.0/shares/${tokenId}/root/children?$top=500`;
    }
    const r = await fetch(graphUrl, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const data = await r.json();
    if (data.error) return res.status(400).json(data);
    const items = (data.value || []).map((item) => ({
      name: item.name,
      id: item.id,
      isFolder: !!item.folder,
      downloadUrl: item['@microsoft.graph.downloadUrl'] || null,
      driveId: (item.parentReference || {}).driveId || driveId
    }));
    res.json({ items });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.get('/health', (req, res) => res.json({ ok: true }));

app.listen(PORT, () => console.log('Proxy running on port', PORT));
