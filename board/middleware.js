// Juku OS directors' PIN gate for the build board (decision 0007 and its addendum).
// Every path on every host of the project passes through here; nothing of the board is served without a valid signed cookie.
// Changing the PIN: rotate BOARD_COOKIE_SECRET at the same time, which ends every remembered session.
export const config = { matcher: '/:path*' };

const COOKIE = 'jukuos_board';
const DAYS = 30;
const ROBOTS = 'noindex, nofollow';
const enc = new TextEncoder();

async function hmac(secret, msg) {
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const sig = await crypto.subtle.sign('HMAC', key, enc.encode(msg));
  return [...new Uint8Array(sig)].map(b => b.toString(16).padStart(2, '0')).join('');
}
async function sha256(msg) {
  const h = await crypto.subtle.digest('SHA-256', enc.encode(msg));
  return [...new Uint8Array(h)].map(b => b.toString(16).padStart(2, '0')).join('');
}
function same(a, b) {
  if (a.length !== b.length) return false;
  let r = 0; for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}
function readCookie(req, name) {
  const c = req.headers.get('cookie') || '';
  const m = c.split(/;\s*/).find(p => p.startsWith(name + '='));
  return m ? decodeURIComponent(m.slice(name.length + 1)) : null;
}
async function valid(req, secret) {
  const v = readCookie(req, COOKIE);
  if (!v) return false;
  const [exp, sig] = v.split('.');
  if (!exp || !sig || Number(exp) < Date.now()) return false;
  return same(sig, await hmac(secret, exp));
}
function pinPage(wrong) {
  return new Response(`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#06070f"><title>Juku OS</title>
<style>:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;background:#06070f;background-image:radial-gradient(ellipse 80% 50% at 50% -10%,rgba(83,234,253,.08),transparent 60%);color:#f2f4f7;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;padding:24px}
form{width:100%;max-width:300px;display:grid;gap:14px;text-align:center}.e{font:500 11px ui-monospace,Menlo,monospace;letter-spacing:.22em;text-transform:uppercase;color:#6b7684}h1{margin:0;font-size:22px;font-weight:600}
input{font:500 28px ui-monospace,Menlo,monospace;letter-spacing:.5em;text-align:center;padding:14px 0 14px .5em;border-radius:10px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.04);color:#f2f4f7;outline:none;width:100%}input:focus{border-color:#53eafd;box-shadow:0 0 0 3px rgba(83,234,253,.18)}
button{font:600 15px system-ui,sans-serif;padding:13px;border-radius:10px;border:0;background:#53eafd;color:#06070f;cursor:pointer}.w{color:#ff9b9b;font-size:13px;min-height:1em}</style></head>
<body><form method="post" action="/__pin"><div class="e">Juku OS</div><h1>Directors only</h1><input name="pin" inputmode="numeric" pattern="[0-9]*" maxlength="8" autocomplete="off" autofocus aria-label="Directors' PIN"><div class="w">${wrong ? 'That PIN is not right.' : ''}</div><button type="submit">Open the board</button></form></body></html>`,
    { status: wrong ? 401 : 200, headers: { 'content-type': 'text/html; charset=utf-8', 'x-robots-tag': ROBOTS, 'cache-control': 'private, no-store' } });
}

export default async function middleware(req) {
  const url = new URL(req.url);
  const secret = process.env.BOARD_COOKIE_SECRET;
  const pinHash = process.env.BOARD_PIN_SHA256;
  const salt = process.env.BOARD_PIN_SALT || '';
  if (!secret || !pinHash) return new Response('Not configured.', { status: 503, headers: { 'x-robots-tag': ROBOTS } });

  if (url.pathname === '/robots.txt') return; // robots.txt says "Allow: /" so crawlers can read the noindex on the PIN response

  if (url.pathname === '/__pin' && req.method === 'POST') {
    const form = await req.formData().catch(() => null);
    const pin = String(form?.get('pin') || '').trim();
    if (pin && same(await sha256(salt + pin), pinHash)) {
      const exp = String(Date.now() + DAYS * 864e5);
      const v = exp + '.' + (await hmac(secret, exp));
      return new Response(null, { status: 303, headers: {
        location: '/', 'x-robots-tag': ROBOTS, 'cache-control': 'private, no-store',
        'set-cookie': `${COOKIE}=${encodeURIComponent(v)}; Path=/; Max-Age=${DAYS * 86400}; HttpOnly; Secure; SameSite=Strict` } });
    }
    await new Promise(r => setTimeout(r, 1200)); // slows a single guesser; the attempt limit is the project's firewall rule (10 a minute per address on POST /__pin)
    return pinPage(true);
  }

  if (!(await valid(req, secret))) return pinPage(false);
  // authorised: fall through to the static file
}
