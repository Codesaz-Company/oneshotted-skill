#!/usr/bin/env python3
"""Oneshotted library from the command line: real motion pieces made by AI agents, with their exact prompts.

    python3 scripts/library.py search "kinetic typography launch" [--limit 8] [--kind video] [--framework remotion]
    python3 scripts/library.py recipe <id> [--chars 6000]        # the full prompt, tags, duration, credit
    python3 scripts/library.py frames <id> [--count 3] [--out refs]  # keyframes saved as JPGs: Read them
    python3 scripts/library.py similar <id> [--limit 6]           # pieces that LOOK alike
    python3 scripts/library.py filters                            # valid filter values
    python3 scripts/library.py login                              # sign in with your Oneshotted account (browser)
    python3 scripts/library.py logout

Only VERIFIED owner prompts reviewed as full references: the creator quoted this exact prompt on X, and a review
found it carries real direction (prompt_use "full"; "weak" ones like "Go all out." and unreviewed ones are skipped).
Search and similar keep only those pieces; recipe drops any other prompt (rebuilt by Oneshotted, "likely",
"unconfirmed", "partial"), so the agent never builds on a prompt the creator didn't write.
--any shows everything: style references to look at, never prompts to adapt.
Authentication, same as the Oneshotted MCP: sign in once with `login` (OAuth in your browser; the token is kept in
~/.config/oneshotted/token.json, readable only by you, and refreshed automatically), or set an API key from
https://oneshotted.io/mcp-docs in ONESHOTTED_API_KEY (or ~/.config/oneshotted/key). Calls count toward your account.
Standard library only. Free plan: 30 recipe/frames calls a day, so pick 1-2 references, not 20.
"""
import argparse, base64, hashlib, http.server, json, os, pathlib, secrets, sys, tempfile, threading, time, urllib.error, urllib.parse, urllib.request, webbrowser

ENDPOINT = os.environ.get('ONESHOTTED_ENDPOINT', 'https://oneshotted.io/mcp')
SITE = urllib.parse.urlsplit(ENDPOINT)._replace(path='', query='', fragment='').geturl()
CONF = pathlib.Path.home() / '.config/oneshotted'
TOKEN = CONF / 'token.json'
UA = {'User-Agent': 'oneshotted-skill/0.3.0'}


def post_form(url, data):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), method='POST', headers=UA | {'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def save_token(t):
    CONF.mkdir(mode=0o700, parents=True, exist_ok=True)
    t['expires_at'] = time.time() + int(t.get('expires_in', 3600)) - 60
    os.chmod(CONF, 0o700)
    fd, tmp = tempfile.mkstemp(dir=CONF, prefix='.token-')  # created 0600, unique per process
    with os.fdopen(fd, 'w') as f:
        json.dump(t, f)
    os.replace(tmp, TOKEN)  # never a half-written token file


def read_token():
    try:
        t = json.loads(TOKEN.read_text())
    except (OSError, ValueError):
        return None
    return t if isinstance(t, dict) and t.get('access_token') else None


def login():
    """OAuth authorization code + PKCE with a loopback redirect (RFC 8252), exactly what MCP clients do."""
    try:
        meta = json.loads(urllib.request.urlopen(urllib.request.Request(SITE + '/.well-known/oauth-authorization-server', headers=UA), timeout=30).read())
    except (OSError, ValueError) as e:
        sys.exit(f'Could not reach Oneshotted to sign in ({getattr(e, "reason", e)}).')
    got = {}

    class Back(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            u = urllib.parse.urlsplit(self.path)
            if u.path != '/callback':
                self.send_response(404); self.end_headers(); return
            q = urllib.parse.parse_qs(u.query)
            got.update({k: v[0] for k, v in q.items() if k in ('code', 'state', 'error')})
            self.send_response(200); self.send_header('Content-Type', 'text/html; charset=utf-8'); self.end_headers()
            ok = 'code' in got
            self.wfile.write(('<h2>' + ('Signed in. You can close this tab.' if ok else 'Sign-in was cancelled.') + '</h2>').encode())

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(('127.0.0.1', 0), Back)
    srv.timeout = 300  # handle_request gives up on its own: no thread left blocked on a closed socket
    redirect = f'http://127.0.0.1:{srv.server_port}/callback'
    # One registered client per machine, reused (loopback redirects match on any port, RFC 8252).
    saved = CONF / 'client.json'
    client = None
    try:
        client = json.loads(saved.read_text())
    except (OSError, ValueError):
        pass
    if not isinstance(client, dict) or not client.get('client_id'):
        try:
            client = json.loads(urllib.request.urlopen(urllib.request.Request(meta['registration_endpoint'], method='POST',
                data=json.dumps({'client_name': 'Oneshotted skill', 'redirect_uris': ['http://127.0.0.1/callback']}).encode(),
                headers=UA | {'Content-Type': 'application/json', 'Accept': 'application/json'}), timeout=30).read())
        except (OSError, ValueError, KeyError) as e:
            sys.exit(f'Could not register with Oneshotted to sign in ({getattr(e, "reason", e)}).')
        CONF.mkdir(mode=0o700, parents=True, exist_ok=True)
        saved.write_text(json.dumps({'client_id': client['client_id']}))
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()
    state = secrets.token_urlsafe(16)
    url = meta['authorization_endpoint'] + '?' + urllib.parse.urlencode({'client_id': client['client_id'], 'redirect_uri': redirect, 'response_type': 'code',
        'scope': 'mcp:use', 'state': state, 'code_challenge': challenge, 'code_challenge_method': 'S256'})
    print('Opening your browser to sign in to Oneshotted. If it does not open, visit:\n' + url, flush=True)
    webbrowser.open(url)
    t = threading.Thread(target=lambda: [srv.handle_request() for _ in range(5) if 'code' not in got and 'error' not in got], daemon=True)
    t.start(); t.join(300); srv.server_close()
    if got.get('state') != state or 'code' not in got:
        reason = ''.join(ch for ch in got.get('error', 'no answer in 5 minutes') if ch.isprintable())[:80]
        sys.exit('Sign-in did not complete (' + reason + ').')
    try:
        tok = post_form(meta['token_endpoint'], {'grant_type': 'authorization_code', 'client_id': client['client_id'], 'redirect_uri': redirect,
                                                 'code_verifier': verifier, 'code': got['code']})
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors='replace')
        if e.code == 401 or 'invalid_client' in body:
            (CONF / 'client.json').unlink(missing_ok=True)  # a stale client: the next login registers a fresh one
        sys.exit(f'Sign-in failed at the token step ({e.code}). Run login again.')
    except OSError as e:
        sys.exit(f'Could not reach Oneshotted to finish signing in ({getattr(e, "reason", e)}).')
    tok['client_id'], tok['token_endpoint'] = client['client_id'], meta['token_endpoint']
    save_token(tok)
    print('Signed in. Calls now count toward your Oneshotted account.')
    if os.environ.get('ONESHOTTED_API_KEY') or (CONF / 'key').exists():
        print('Note: an API key is also set (ONESHOTTED_API_KEY or ~/.config/oneshotted/key) and is used first; remove it to use this sign-in.')


USING = 'none'  # which credential the last key() returned: 'key' or 'token'


def key():
    global USING
    k = os.environ.get('ONESHOTTED_API_KEY', '').strip()
    p = CONF / 'key'
    if not k and p.exists():
        k = p.read_text().strip()
    if k:
        USING = 'key'
        return k
    t = read_token()
    if t:  # signed in: refresh the hour-long access token when it's about to expire
        USING = 'token'
        if time.time() < t.get('expires_at', 0):
            return t['access_token']
        for attempt in range(2):
            try:
                n = post_form(t['token_endpoint'], {'grant_type': 'refresh_token', 'refresh_token': t['refresh_token'], 'client_id': t['client_id']})
                n['client_id'], n['token_endpoint'] = t['client_id'], t['token_endpoint']
                save_token(n)
                return n['access_token']
            except urllib.error.HTTPError:
                # Another call may have refreshed it a moment ago (refresh tokens rotate): read the file again once.
                time.sleep(0.5)
                fresh = read_token()
                if fresh and time.time() < fresh.get('expires_at', 0):
                    return fresh['access_token']
                t = fresh or t
            except (OSError, KeyError, ValueError):
                sys.exit('Could not reach Oneshotted to renew your sign-in. Check the connection and retry.')
        sys.exit('Your Oneshotted sign-in expired. Run: python3 scripts/library.py login')
    sys.exit('Not signed in to Oneshotted. Run: python3 scripts/library.py login   (or set ONESHOTTED_API_KEY to a key from https://oneshotted.io/mcp-docs)')


def usable(r):
    return r.get('prompt') == 'verified' and r.get('prompt_use') == 'full'


def call(tool, args):
    body = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {'name': tool, 'arguments': args}}).encode()
    req = urllib.request.Request(ENDPOINT, data=body, method='POST', headers={
        'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream',
        'Authorization': 'Bearer ' + key(), 'User-Agent': 'oneshotted-skill/0.3.0'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode()
    except urllib.error.HTTPError as e:
        if e.code == 401:
            if USING == 'token':  # only a rejected sign-in is cleared; a bad API key is the key's problem
                TOKEN.unlink(missing_ok=True)
                sys.exit('Your Oneshotted sign-in is no longer valid. Run: python3 scripts/library.py login')
            sys.exit('Oneshotted rejected the API key (ONESHOTTED_API_KEY or ~/.config/oneshotted/key). Check it at https://oneshotted.io/mcp-docs')
        sys.exit(f'Oneshotted answered {e.code}: {e.read().decode()[:300]}')
    except OSError as e:  # URLError, read timeouts (socket.timeout is not TimeoutError before 3.10)
        sys.exit(f'Could not reach Oneshotted ({getattr(e, "reason", e)}). Continue without the library and say so.')
    if raw.startswith('event:') or raw.startswith('data:'):  # an SSE reply: the last data line is the message
        data = [l[5:].strip() for l in raw.splitlines() if l.startswith('data:')]
        raw = data[-1] if data else ''
    try:
        msg = json.loads(raw)
    except ValueError:
        sys.exit('Oneshotted sent an unreadable reply. Continue without the library and say so.')
    if 'error' in msg:
        sys.exit('Oneshotted error: ' + msg['error'].get('message', str(msg['error'])))
    res = msg['result']
    if res.get('isError'):
        sys.exit(' '.join(c.get('text', '') for c in res.get('content', [])))  # a limit or a bad id: say it as is
    return res


def text_of(res):
    if res.get('structuredContent') is not None:
        return json.dumps(res['structuredContent'], indent=1, ensure_ascii=False)
    return '\n'.join(c['text'] for c in res.get('content', []) if c.get('type') == 'text')


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = a.add_subparsers(dest='cmd', required=True)
    p = s.add_parser('search'); p.add_argument('query'); p.add_argument('--limit', type=int, default=8)
    p.add_argument('--any', action='store_true', help='include pieces without a verified owner prompt')
    for f in ('kind', 'framework', 'model', 'motion_type'):
        p.add_argument('--' + f)
    p = s.add_parser('recipe'); p.add_argument('id'); p.add_argument('--chars', type=int, default=6000)
    p.add_argument('--any', action='store_true', help='keep prompts that are not the verified owner prompt')
    p = s.add_parser('frames'); p.add_argument('id'); p.add_argument('--count', type=int, default=3); p.add_argument('--out', default='refs')
    p = s.add_parser('similar'); p.add_argument('id'); p.add_argument('--limit', type=int, default=6)
    s.add_parser('filters'); s.add_parser('login'); s.add_parser('logout')
    o = a.parse_args()

    if o.cmd == 'login':
        return login()
    if o.cmd == 'logout':
        TOKEN.unlink(missing_ok=True)
        return print('Signed out on this machine. To end the app connection everywhere, disconnect "Oneshotted skill" on your dashboard.')

    if o.cmd == 'search':
        args = {'query': o.query, 'limit': min(o.limit, 20)} | ({} if o.any else {'strong_prompt': True}) | {f: getattr(o, f) for f in ('kind', 'framework', 'model', 'motion_type') if getattr(o, f)}
        res = call('search_motion', args)
        data = res.get('structuredContent')
        if data is None:
            print(text_of(res)); return
        if not o.any:  # verified owner prompts only, without the rebuilt fields
            keep = [{k: v for k, v in r.items() if not k.startswith('rebuilt_') and k != 'prompt_use'} for r in data.get('results', []) if usable(r)]
            data = {'count': len(keep[:o.limit]), 'results': keep[:o.limit],
                    'note': "Only pieces whose creator's own verified prompt is a full reference. Try other words, or --any for style-only references."}
        print(json.dumps(data, indent=1, ensure_ascii=False))
    elif o.cmd == 'recipe':
        res = call('get_recipe', {'id': o.id, 'max_prompt_chars': max(500, o.chars)})
        data = res.get('structuredContent')
        if data is not None and not o.any:
            data = {k: v for k, v in data.items() if not k.startswith('rebuilt')}  # never Oneshotted's reconstruction
            p = data.get('prompt')
            if not isinstance(p, dict) or p.get('status') != 'verified' or p.get('use') != 'full':
                data['prompt'] = {'note': "No full verified prompt from the creator: use this piece as a style reference only, don't adapt a prompt."}
            else:
                data['prompt'] = {k: v for k, v in p.items() if k != 'use'}
            print(json.dumps(data, indent=1, ensure_ascii=False))
        else:
            print(text_of(res))
    elif o.cmd == 'similar':
        res = call('find_similar', {'id': o.id, 'limit': min(max(o.limit, 1), 12)})
        data = res.get('structuredContent')
        if data is None:
            print(text_of(res)); return
        for r in data.get('results', []):  # everything that looks alike, marked: only "prompt": "usable" ones may be adapted
            for k in [k for k in r if k.startswith('rebuilt_')]:
                del r[k]
            r['prompt'] = 'usable' if usable(r) else 'style reference only'
            r.pop('prompt_use', None); r.pop('prompt_chars', None) if r['prompt'] != 'usable' else None
        print(json.dumps(data, indent=1, ensure_ascii=False))
    elif o.cmd == 'filters':
        print(text_of(call('list_filters', {})))
    elif o.cmd == 'frames':
        res = call('get_keyframes', {'id': o.id, 'count': max(1, min(o.count, 5))})
        out = pathlib.Path(o.out); out.mkdir(parents=True, exist_ok=True)
        label, n = '', 0
        for c in res.get('content', []):
            if c.get('type') == 'text':
                label = c['text']
                print(label)
            elif c.get('type') == 'image':
                n += 1
                f = out / f"{''.join(ch if ch.isalnum() or ch in '-_' else '-' for ch in o.id)}-{n}.jpg"
                f.write_bytes(base64.b64decode(c['data']))
                print(f'  saved {f}')
        if not n:
            print('No keyframes for this piece.')


if __name__ == '__main__':
    main()
