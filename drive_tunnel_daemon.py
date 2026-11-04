#!/usr/bin/env python3
"""
Daemon Tunnel Cloud & Serveur de Fichiers pour Mon Drive Privé (774 documents) :
1. Sert les 774 documents importants en streaming HTTP/HTTPS (avec support Range pour PDF iOS Safari) sur le port 8795.
2. Maintient un tunnel Cloudflare HTTPS permanent (`cloudflared tunnel --url http://127.0.0.1:8795`).
3. Met à jour `endpoint.json` et le pousse automatiquement sur GitHub Pages (`annuaire-prive`)
   pour que l'application sur le Tapp Store se connecte automatiquement au Mac en Wi-Fi comme en 4G/5G.
"""
import csv
import glob
import hashlib
import http.server
import json
import mimetypes
import os
import re
import subprocess
import threading
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path("/Users/thomaslefevre/.t3/projects/projet-regroup")
LOCAL_DOCS_DIR = ROOT_DIR / "Documents_Importants"
ICLOUD_DOCS_DIR = Path("/Users/thomaslefevre/Library/Mobile Documents/com~apple~CloudDocs/Documents_Importants_Thomas_Lefevre")
ENDPOINT_JSON = ROOT_DIR / "endpoint.json"

PORT = 8795
LAN_URL = f"http://192.168.1.111:{PORT}"
LOCAL_URL = f"http://127.0.0.1:{PORT}"

DEFAULT_PIN = "1818"
VALID_TOKEN = hashlib.sha256(f"drive-tunnel-{DEFAULT_PIN}".encode("utf-8")).hexdigest()[:32]

current_tunnel_url = ""


def is_authorized(query_params: dict, headers) -> bool:
    pin = (query_params.get("pin", [""])[0] or headers.get("X-Pin") or "").strip()
    token = (query_params.get("token", [""])[0] or headers.get("X-Token") or "").strip()
    if pin == DEFAULT_PIN or token == VALID_TOKEN:
        return True
    return False


def load_docs_index() -> list:
    docs = []
    seen_paths = set()
    csv_path = ROOT_DIR / "INDEX_DOCUMENTS.csv"
    if csv_path.exists():
        with open(csv_path, encoding="utf-8-sig") as f:
            for idx, row in enumerate(csv.DictReader(f), 1):
                cat = (row.get("category") or row.get("categorie") or "").strip()
                fname = (row.get("filename") or row.get("fichier") or "").strip()
                if not cat or not fname:
                    continue
                rel_path = f"Documents_Importants/{cat}/{fname}"
                seen_paths.add((cat, fname))
                sender_name = (row.get("sender_name") or "").strip()
                sender_email = (row.get("sender_email") or "").strip()
                sender = f"{sender_name} <{sender_email}>".strip(" <>") if (sender_name or sender_email) else (row.get("expediteur") or "").strip()
                docs.append({
                    "id": f"d_{idx}",
                    "cat": cat,
                    "date": (row.get("date") or "").strip(),
                    "file": fname,
                    "subject": (row.get("subject") or row.get("sujet_mail") or "").strip(),
                    "sender": sender,
                    "account": (row.get("account") or "").strip(),
                    "size_kb": (row.get("size_kb") or row.get("taille_ko") or "").strip(),
                    "path": rel_path,
                })

    # Scan for any new files added on disk in LOCAL_DOCS_DIR or ICLOUD_DOCS_DIR
    for base_dir in (LOCAL_DOCS_DIR, ICLOUD_DOCS_DIR):
        if not base_dir.exists():
            continue
        for cat_dir in sorted(base_dir.iterdir()):
            if not cat_dir.is_dir() or cat_dir.name.startswith("."):
                continue
            cat = cat_dir.name
            for fpath in sorted(cat_dir.iterdir()):
                if not fpath.is_file() or fpath.name.startswith("."):
                    continue
                if (cat, fpath.name) in seen_paths:
                    continue
                seen_paths.add((cat, fpath.name))
                st = fpath.stat()
                dt_str = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d")
                docs.append({
                    "id": f"d_{len(docs) + 1}",
                    "cat": cat,
                    "date": dt_str,
                    "file": fpath.name,
                    "subject": "Fichier ajouté dans le Drive",
                    "sender": "iCloud Drive / Mac",
                    "account": "Drive",
                    "size_kb": f"{st.st_size / 1024:.1f}",
                    "path": f"Documents_Importants/{cat}/{fpath.name}",
                })
    return docs


def resolve_doc_file(rel_path: str):
    clean = urllib.parse.unquote(rel_path).lstrip("/")
    if clean.startswith("files/"):
        clean = clean[len("files/"):]
    if clean.startswith("Documents_Importants/"):
        clean = clean[len("Documents_Importants/"):]

    parts = Path(clean).parts
    if not parts or ".." in parts:
        return None

    for base_dir in (LOCAL_DOCS_DIR, ICLOUD_DOCS_DIR):
        candidate = (base_dir / Path(*parts)).resolve()
        try:
            candidate.relative_to(base_dir.resolve())
            if candidate.is_file():
                return candidate
        except ValueError:
            continue
    return None


class DriveTunnelHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send_cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Range, X-Pin, X-Token")
        self.send_header("Access-Control-Expose-Headers", "Content-Length, Content-Range, Accept-Ranges, Content-Disposition")

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._send_cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_HEAD(self) -> None:
        self._handle_request(head_only=True)

    def do_GET(self) -> None:
        self._handle_request(head_only=False)

    def _send_json(self, status: int, payload: dict, head_only: bool = False) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self._send_cors()
        self.end_headers()
        if not head_only:
            self.wfile.write(raw)

    def _serve_file(self, fpath: Path, download: bool = False, head_only: bool = False, cache: bool = False) -> None:
        try:
            file_size = fpath.stat().st_size
        except OSError:
            self._send_json(404, {"error": "File not found"}, head_only=head_only)
            return

        ctype, _ = mimetypes.guess_type(str(fpath))
        if not ctype:
            ext = fpath.suffix.lower()
            if ext == ".pdf":
                ctype = "application/pdf"
            elif ext in (".jpg", ".jpeg"):
                ctype = "image/jpeg"
            elif ext == ".png":
                ctype = "image/png"
            elif ext == ".svg":
                ctype = "image/svg+xml"
            else:
                ctype = "application/octet-stream"

        disp_type = "attachment" if download else "inline"
        safe_name = urllib.parse.quote(fpath.name)

        range_header = self.headers.get("Range")
        start, end = 0, file_size - 1
        status = 200

        if range_header and range_header.startswith("bytes=") and file_size > 0:
            try:
                r_part = range_header.replace("bytes=", "").split(",")[0].strip()
                s_str, e_str = r_part.split("-")
                if s_str:
                    start = int(s_str)
                    end = int(e_str) if e_str else file_size - 1
                elif e_str:
                    start = max(0, file_size - int(e_str))
                    end = file_size - 1
                start = max(0, min(start, file_size - 1))
                end = max(start, min(end, file_size - 1))
                status = 206
            except Exception:
                start, end = 0, file_size - 1
                status = 200

        length = (end - start + 1) if file_size > 0 else 0

        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(length))
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
        self.send_header(
            "Content-Disposition",
            f"{disp_type}; filename=\"{fpath.name.encode('ascii', 'ignore').decode('ascii') or 'document'}\"; filename*=UTF-8''{safe_name}",
        )
        self.send_header("Cache-Control", "public, max-age=3600" if cache else "no-cache")
        self._send_cors()
        self.end_headers()

        if head_only or length <= 0:
            return

        with open(fpath, "rb") as f:
            f.seek(start)
            remaining = length
            chunk_size = 64 * 1024
            while remaining > 0:
                chunk = f.read(min(chunk_size, remaining))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    break
                remaining -= len(chunk)

    def _handle_request(self, head_only: bool = False) -> None:
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        path = parsed.path

        if path == "/api/status":
            self._send_json(
                200,
                {
                    "ok": True,
                    "service": "mon-drive-tunnel",
                    "tunnelUrl": current_tunnel_url,
                    "lanUrl": LAN_URL,
                    "localUrl": LOCAL_URL,
                    "updatedAt": datetime.now(timezone.utc).isoformat(),
                },
                head_only=head_only,
            )
            return

        if path == "/api/docs":
            if not is_authorized(query, self.headers):
                self._send_json(401, {"error": "Code PIN requis"}, head_only=head_only)
                return
            docs = load_docs_index()
            self._send_json(
                200,
                {
                    "ok": True,
                    "count": len(docs),
                    "docs": docs,
                },
                head_only=head_only,
            )
            return

        if path.startswith("/files/") or path.startswith("/Documents_Importants/"):
            if not is_authorized(query, self.headers):
                self._send_json(401, {"error": "Code PIN requis pour ouvrir ce document"}, head_only=head_only)
                return
            target = resolve_doc_file(path)
            if not target:
                self._send_json(404, {"error": "Document introuvable sur le Mac"}, head_only=head_only)
                return
            download = query.get("download", ["0"])[0] == "1"
            self._serve_file(target, download=download, head_only=head_only, cache=True)
            return

        # Static PWA files at root
        static_map = {
            "/": ROOT_DIR / "index.html",
            "/index.html": ROOT_DIR / "index.html",
            "/manifest.json": ROOT_DIR / "manifest.json",
            "/sw.js": ROOT_DIR / "sw.js",
            "/icon.svg": ROOT_DIR / "icon.svg",
            "/apple-touch-icon.png": ROOT_DIR / "apple-touch-icon.png",
            "/vault.enc.json": ROOT_DIR / "vault.enc.json",
            "/endpoint.json": ROOT_DIR / "endpoint.json",
            "/assets/icon.svg": ROOT_DIR / "assets" / "icon.svg",
            "/assets/apple-touch-icon.png": ROOT_DIR / "assets" / "apple-touch-icon.png",
        }
        if path in static_map and static_map[path].is_file():
            self._serve_file(static_map[path], download=False, head_only=head_only, cache=False)
            return

        self._send_json(404, {"error": "Not found"}, head_only=head_only)

    def log_message(self, format: str, *args) -> None:
        pass


def save_and_push_endpoint(tunnel_url: str) -> None:
    global current_tunnel_url
    current_tunnel_url = tunnel_url
    try:
        if ENDPOINT_JSON.exists():
            existing = json.loads(ENDPOINT_JSON.read_text(encoding="utf-8"))
            if existing.get("tunnelUrl") == tunnel_url and existing.get("lanUrl") == LAN_URL:
                return
    except Exception:
        pass

    payload = {
        "tunnelUrl": tunnel_url,
        "lanUrl": LAN_URL,
        "localUrl": LOCAL_URL,
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }
    ENDPOINT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    try:
        subprocess.run(["git", "add", "endpoint.json"], cwd=str(ROOT_DIR), check=True)
        diff = subprocess.run(["git", "diff", "--cached", "--quiet", "--", "endpoint.json"], cwd=str(ROOT_DIR))
        if diff.returncode != 0:
            subprocess.run(
                ["git", "commit", "-m", "chore(tunnel): update live Drive cloudflare tunnel endpoint"],
                cwd=str(ROOT_DIR),
                check=True,
            )
            subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(ROOT_DIR))
            subprocess.run(["git", "push", "origin", "main"], cwd=str(ROOT_DIR), check=True)
    except Exception as e:
        print("Git sync error:", e, flush=True)


def run_tunnel_forever() -> None:
    cf_candidates = glob.glob(os.path.expanduser("~/.t3/tools/cloudflared/*/*/cloudflared"))
    if not cf_candidates:
        cf_candidates = glob.glob("/Users/thomaslefevre/.t3/projects/*/.bin/cloudflared")
    if not cf_candidates:
        print("cloudflared binary not found", flush=True)
        return
    cf_bin = cf_candidates[0]

    while True:
        try:
            proc = subprocess.Popen(
                [cf_bin, "tunnel", "--url", f"http://127.0.0.1:{PORT}", "--no-autoupdate"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            for line in proc.stdout:
                m = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
                if m:
                    url = m.group(0)
                    print("Active Drive Tunnel URL:", url, flush=True)
                    save_and_push_endpoint(url)
            proc.wait()
        except Exception as e:
            print("Tunnel error:", e, flush=True)
        time.sleep(5)


def main() -> None:
    threading.Thread(target=run_tunnel_forever, daemon=True).start()
    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), DriveTunnelHandler)
    print(f"Drive Tunnel Server listening on http://0.0.0.0:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
