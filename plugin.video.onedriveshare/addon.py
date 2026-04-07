# -*- coding: utf-8 -*-
import json
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

ADDON_ID = 'plugin.video.onedriveshare'
addon = xbmcaddon.Addon(ADDON_ID)
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

VIDEO_EXT = (
    '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.m4v', '.mpg', '.mpeg', '.ts', '.m2ts', '.flv', '.webm',
)
SUBTITLE_EXT = ('.srt', '.sub', '.ass', '.ssa', '.vtt')


def dbg(msg):
    try:
        path = xbmcvfs.translatePath('special://temp/onedriveshare_debug.log')
        with open(path, 'a', encoding='utf-8') as f:
            f.write(time.strftime('%Y-%m-%d %H:%M:%S ') + msg + '\n')
    except Exception:
        pass


def get_params():
    q = sys.argv[2][1:] if len(sys.argv) > 2 and sys.argv[2].startswith('?') else ''
    return dict(urllib.parse.parse_qsl(q, keep_blank_values=True))


def share_url():
    return addon.getSetting('share_url').strip()


def root_menu_items():
    su = share_url()
    items = []
    if su:
        items.append(
            (
                'Videos',
                BASE_URL + '?' + urllib.parse.urlencode({'mode': 'browse'}),
                True,
            )
        )
    else:
        items.append(
            (
                'Set share URL (Addon settings)',
                BASE_URL + '?' + urllib.parse.urlencode({'mode': 'settings'}),
                True,
            )
        )
    items.append(
        (
            'Pair with phone',
            BASE_URL + '?' + urllib.parse.urlencode({'mode': 'pair'}),
            True,
        )
    )
    items.append(
        (
            'View debug log',
            BASE_URL + '?' + urllib.parse.urlencode({'mode': 'log'}),
            True,
        )
    )
    return items


def add_dirs(items):
    for name, url, is_folder in items:
        li = xbmcgui.ListItem(name)
        xbmcplugin.addDirectoryItem(HANDLE, url, li, is_folder)
    xbmcplugin.endOfDirectory(HANDLE)


def do_settings():
    addon.openSettings()
    xbmc.executebuiltin('Container.Refresh')


def show_log():
    path = xbmcvfs.translatePath('special://temp/onedriveshare_debug.log')
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()[-200:]
        text = ''.join(lines) or '(empty — nothing logged yet)'
    except Exception as e:
        text = 'Could not read log: ' + str(e)
    xbmcgui.Dialog().textviewer('onedriveshare debug log', text)


def do_pair():
    pin = '%04d' % random.randint(0, 9999)
    dbg('pair started pin=' + pin)
    dlg = xbmcgui.DialogProgress()
    dlg.create('Pair with phone', 'PIN: [B]' + pin + '[/B]\nOn your phone open the setup page and send your link.')
    topic = 'kodi-pair-' + pin
    seen = set()
    pair_start = int(time.time())
    for i in range(90):
        if dlg.iscanceled():
            dlg.close()
            return
        dlg.update(int(100 * i / 90), 'Waiting for phone (same WiFi / internet)...')
        xbmc.sleep(2000)
        try:
            req = urllib.request.Request(
                'https://ntfy.sh/' + topic + '/json',
                headers={'User-Agent': 'Kodi-OneDrive-Share'},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode('utf-8')
            if not raw.strip():
                continue
            msgs = json.loads(raw)
            if not isinstance(msgs, list):
                msgs = [msgs]
            for m in msgs:
                mid = m.get('id')
                if mid in seen:
                    continue
                seen.add(mid)
                if m.get('event') not in (None, 'message'):
                    continue
                body = (m.get('message') or '').strip()
                if not body.startswith('http'):
                    continue
                mt = m.get('time')
                if mt is not None:
                    try:
                        if int(mt) < pair_start - 120:
                            continue
                    except (TypeError, ValueError):
                        pass
                addon.setSetting('share_url', body)
                dbg('pair saved url len=' + str(len(body)))
                dlg.close()
                xbmcgui.Dialog().ok('OneDrive Share', 'Share URL saved from your phone.')
                xbmc.executebuiltin('Container.Refresh')
                return
        except Exception as e:
            dbg('pair poll error: ' + str(e))
    dlg.close()
    xbmcgui.Dialog().ok('OneDrive Share', 'Timed out waiting for the setup page. Try again.')


def is_video(name):
    lower = name.lower()
    return any(lower.endswith(ext) for ext in VIDEO_EXT)


def is_subtitle(name):
    lower = name.lower()
    return any(lower.endswith(ext) for ext in SUBTITLE_EXT)


def browse(folder_id=None, drive_id=None):
    su = share_url()
    if not su:
        xbmcgui.Dialog().ok('OneDrive Share', 'Set your SharePoint link in addon settings or pair with phone.')
        xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
        return
    from resources.lib import config

    try:
        items = config.get_files(su, subfolder=folder_id, drive_id=drive_id)
    except Exception as e:
        dbg('get_files error: ' + str(e))
        xbmcgui.Dialog().ok('OneDrive Share', 'Could not load folder:\n' + str(e))
        xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
        return

    subs = [it for it in items if not it.get('isFolder') and is_subtitle(it.get('name', ''))]
    sub_by_base = {}
    for s in subs:
        base = os.path.splitext(s.get('name', ''))[0].lower()
        sub_by_base[base] = s.get('downloadUrl')

    for it in items:
        name = it.get('name') or ''
        if it.get('isFolder'):
            q = urllib.parse.urlencode(
                {
                    'mode': 'browse',
                    'folder_id': it.get('id') or '',
                    'drive_id': it.get('driveId') or drive_id or '',
                }
            )
            li = xbmcgui.ListItem(label=name)
            xbmcplugin.addDirectoryItem(HANDLE, BASE_URL + '?' + q, li, True)
            continue
        if not is_video(name):
            continue
        play_url = it.get('downloadUrl')
        if not play_url:
            continue
        base = os.path.splitext(name)[0].lower()
        sub_url = sub_by_base.get(base)
        q = urllib.parse.urlencode({'action': 'play', 'url': play_url})
        if sub_url:
            q += '&' + urllib.parse.urlencode({'sub': sub_url})
        li = xbmcgui.ListItem(label=name)
        li.setProperty('IsPlayable', 'true')
        info = li.getVideoInfoTag()
        info.setTitle(name)
        xbmcplugin.addDirectoryItem(HANDLE, BASE_URL + '?' + q, li, False)

    xbmcplugin.setContent(HANDLE, 'videos')
    xbmcplugin.endOfDirectory(HANDLE)


def do_play(params):
    url = params.get('url')
    if not url:
        xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())
        return
    url = urllib.parse.unquote(url)
    sub = params.get('sub')
    li = xbmcgui.ListItem(path=url)
    li.setContentLookup(False)
    if sub:
        sub = urllib.parse.unquote(sub)
        li.setSubtitles([sub])
    xbmcplugin.setResolvedUrl(HANDLE, True, li)


def main():
    params = get_params()
    dbg('route params=' + json.dumps(params))

    if params.get('action') == 'seturl':
        u = params.get('url') or ''
        u = urllib.parse.unquote(u)
        if u:
            addon.setSetting('share_url', u)
            dbg('seturl len=' + str(len(u)))
        xbmcgui.Dialog().notification('OneDrive Share', 'Share URL saved', xbmcgui.NOTIFICATION_INFO, 4000)
        xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
        return

    if params.get('action') == 'play':
        do_play(params)
        return

    mode = params.get('mode')
    if mode == 'settings':
        do_settings()
        xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
        return
    if mode == 'log':
        show_log()
        xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
        return
    if mode == 'pair':
        do_pair()
        xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
        return
    if mode == 'browse':
        browse(params.get('folder_id') or None, params.get('drive_id') or None)
        return

    add_dirs(root_menu_items())


if __name__ == '__main__':
    main()
