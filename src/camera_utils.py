from __future__ import annotationsfrom __future__ import annotations

from typing import Optional, Tuple, List, Dict, Any, Iterablefrom typing import Optional, Tuple

from urllib.parse import urlsplit, urlunsplitfrom urllib.parse import urlsplit, urlunsplit

import cv2import cv2

import timeimport time

import loggingimport logging

import socketimport socket

import osimport os



logger = logging.getLogger(__name__)logger = logging.getLogger(__name__)



# ----------------- Mask / helpers -----------------def _mask_url(u: str) -> str:

    try:

def _mask_url(u: str) -> str:        p = urlsplit(u)

    try:        net = p.netloc

        p = urlsplit(u)        if "@" in net:

        net = p.netloc            net = f"***:***@{net.split('@', 1)[1]}"

        if "@" in net:        return f"{p.scheme}://{net}{p.path}{('?' + p.query) if p.query else ''}"

            net = f"***:***@{net.split('@', 1)[1]}"    except Exception:

        return f"{p.scheme}://{net}{p.path}{('?' + p.query) if p.query else ''}"        return str(u)

    except Exception:

        return str(u)def _tcp_reachable(host: str, port: int, timeout: float = 3.0) -> bool:

    try:

        with socket.create_connection((host, port), timeout=timeout):

def _tcp_reachable(host: str, port: int, timeout: float = 3.0) -> bool:            return True

    try:    except OSError:

        with socket.create_connection((host, port), timeout=timeout):        return False

            return True

    except OSError:def build_url_with_credentials(url: str, username: Optional[str], password: Optional[str]) -> str:

        return False    """Inject credentials into RTSP/HTTP URL if provided; strip fragments like #live."""

    if not url:

# ----------------- URL building -----------------        logger.debug("build_url_with_credentials: empty url")

        return url

def build_url_with_credentials(url: str, username: Optional[str], password: Optional[str]) -> str:    parts = urlsplit(url)

    """Inject credentials into RTSP/HTTP URL if provided; strip fragments like #live."""    scheme, netloc, path, query, _fragment = parts

    if not url:

        logger.debug("build_url_with_credentials: empty url")    # If creds already present, just strip fragment

        return url    if "@" in netloc:

    parts = urlsplit(url)        logger.debug("build_url_with_credentials: creds already present -> %s", _mask_url(url))

    scheme, netloc, path, query, _fragment = parts        return urlunsplit((scheme, netloc, path, query, ""))



    # If creds already present, just strip fragment    username = (username or "").strip()

    if "@" in netloc:    password = (password or "").strip()

        logger.debug("build_url_with_credentials: creds already present -> %s", _mask_url(url))    if not username or not password:

        return urlunsplit((scheme, netloc, path, query, ""))        logger.debug("build_url_with_credentials: missing username/password -> leaving url unchanged")

        return urlunsplit((scheme, netloc, path, query, ""))

    username = (username or "").strip()

    password = (password or "").strip()    new_netloc = f"{username}:{password}@{netloc}"

    if not username or not password:    masked = f"{scheme}://***:***@{netloc}{path}{('?' + query) if query else ''}"

        logger.debug("build_url_with_credentials: missing username/password -> leaving url unchanged")    logger.info("build_url_with_credentials: injected credentials -> %s", masked)

        return urlunsplit((scheme, netloc, path, query, ""))    return urlunsplit((scheme, new_netloc, path, query, ""))



    new_netloc = f"{username}:{password}@{netloc}"def test_camera(source, attempts: int = 30, delay: float = 0.1) -> Tuple[bool, Optional[float], Optional[Tuple[int, int]], Optional[bytes], Optional[str]]:

    masked = f"{scheme}://***:***@{netloc}{path}{('?' + query) if query else ''}"    """Open a camera/stream and try to read one frame.

    logger.info("build_url_with_credentials: injected credentials -> %s", masked)    Returns: (ok, fps, (w,h), jpeg_bytes, error)

    return urlunsplit((scheme, new_netloc, path, query, ""))    """

    # Force FFmpeg backend with TCP and sane timeouts for RTSP

# ----------------- Basic test -----------------    os.environ.setdefault("OPENCV_FFMPEG_CAPTURE_OPTIONS", "rtsp_transport;tcp|max_delay;5000000|stimeout;30000000")

    masked = _mask_url(str(source))

def test_camera(source, attempts: int = 30, delay: float = 0.1) -> Tuple[bool, Optional[float], Optional[Tuple[int, int]], Optional[bytes], Optional[str]]:    logger.info("test_camera: opening source=%s", masked)

    """Open a camera/stream and try to read one frame.

    Returns: (ok, fps, (w,h), jpeg_bytes, error)    # RTSP preflight: reachability and basic path sanity

    """    try:

    # Force FFmpeg backend with TCP and sane timeouts for RTSP        parts = urlsplit(str(source))

    os.environ.setdefault("OPENCV_FFMPEG_CAPTURE_OPTIONS", "rtsp_transport;tcp|max_delay;5000000|stimeout;30000000")        if parts.scheme.lower() == "rtsp":

    masked = _mask_url(str(source))            host = parts.hostname

    logger.info("test_camera: opening source=%s", masked)            port = parts.port or 554

            if host and not _tcp_reachable(host, port, timeout=3.0):

    # RTSP preflight: reachability and basic path sanity                msg = f"RTSP TCP port not reachable ({host}:{port})"

    try:                logger.error("test_camera: %s", msg)

        parts = urlsplit(str(source))                return False, None, None, None, msg

        if parts.scheme.lower() == "rtsp":            if not parts.path or parts.path == "/":

            host = parts.hostname                logger.warning("test_camera: RTSP path is empty; add the stream path (e.g., /Streaming/Channels/101)")

            port = parts.port or 554    except Exception as e:

            if host and not _tcp_reachable(host, port, timeout=3.0):        logger.debug("test_camera: preflight parse error: %s", e)

                msg = f"RTSP TCP port not reachable ({host}:{port})"

                logger.error("test_camera: %s", msg)    cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)

                return False, None, None, None, msg    if not cap.isOpened():

            if not parts.path or parts.path == "/":        logger.error("test_camera: failed to open source")

                logger.warning("test_camera: RTSP path is empty; add the stream path (e.g., /Streaming/Channels/101)")        return False, None, None, None, "Failed to open source"

    except Exception as e:

        logger.debug("test_camera: preflight parse error: %s", e)    # Hint to reduce latency on some backends

    try:

    cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():    except Exception:

        logger.error("test_camera: failed to open source")        pass

        return False, None, None, None, "Failed to open source"

    fps = cap.get(cv2.CAP_PROP_FPS) or None

    # Hint to reduce latency on some backends    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)

    try:    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    except Exception:    jpeg_bytes = None

        pass    ok = False

    err = None

    fps = cap.get(cv2.CAP_PROP_FPS) or None

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)    try:

    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)        for i in range(attempts):

            ret, frame = cap.read()

    jpeg_bytes = None            if ret and frame is not None:

    ok = False                enc_ok, buf = cv2.imencode(".jpg", frame)

    err = None                if enc_ok:

                    jpeg_bytes = buf.tobytes()

    try:                ok = True

        for i in range(attempts):                logger.info("test_camera: first frame received (fps=%s, size=%sx%s, attempt=%s)", fps, w, h, i + 1)

            ret, frame = cap.read()                break

            if ret and frame is not None:            time.sleep(delay)

                enc_ok, buf = cv2.imencode(".jpg", frame)        if not ok:

                if enc_ok:            err = "No frames received"

                    jpeg_bytes = buf.tobytes()            logger.error("test_camera: %s", err)

                ok = True    finally:

                logger.info("test_camera: first frame received (fps=%s, size=%sx%s, attempt=%s)", fps, w, h, i + 1)        cap.release()

                break

            time.sleep(delay)    size = (w, h) if (w and h) else None

        if not ok:    return ok, fps, size, jpeg_bytes, err
            err = "No frames received"
            logger.error("test_camera: %s", err)
    finally:
        cap.release()

    size = (w, h) if (w and h) else None
    return ok, fps, size, jpeg_bytes, err

# ----------------- Discovery helpers -----------------

BRAND_TEMPLATES: Dict[str, List[str]] = {
    "Unknown/Generic": [
        "/Streaming/Channels/101",
        "/Streaming/Channels/102",
        "/h264Preview_01_main",
        "/h264Preview_01_sub",
        "/cam/realmonitor?channel=1&subtype=0",
        "/cam/realmonitor?channel=1&subtype=1",
        "/axis-media/media.amp",
        "/live.sdp",
        "/media/video1",
    ],
    "Hikvision": [
        "/Streaming/Channels/101",
        "/Streaming/Channels/102",
    ],
    "Dahua/Amcrest": [
        "/cam/realmonitor?channel=1&subtype=0",
        "/cam/realmonitor?channel=1&subtype=1",
    ],
    "Reolink": [
        "/h264Preview_01_main",
        "/h264Preview_01_sub",
    ],
    "Axis": [
        "/axis-media/media.amp",
    ],
    "Uniview": [
        "/media/video1",
        "/unicast/c1/s0/live",
    ],
    "Hanwha/Wisenet": [
        "/profile2/media.smp",
        "/profile1/media.smp",
    ],
    "Unifi Protect": [
        "/",  # Needs port 7447 and camera UUID; placeholder
    ],
}

DEFAULT_PORTS: List[int] = [554, 8554, 10554, 5544, 7447]


def _build_rtsp_url(host: str, port: int, path: str, username: Optional[str], password: Optional[str]) -> str:
    host = host.strip()
    auth = ""
    if (username or "").strip() and (password or "").strip():
        auth = f"{username.strip()}:{password.strip()}@"
    return f"rtsp://{auth}{host}:{port}{path}"


def generate_common_rtsp_urls(host: str, username: Optional[str], password: Optional[str], brand: str = "Unknown/Generic", ports: Optional[Iterable[int]] = None) -> List[str]:
    templates = BRAND_TEMPLATES.get(brand, BRAND_TEMPLATES["Unknown/Generic"]) or []
    ports_list = list(ports) if ports is not None else DEFAULT_PORTS
    urls: List[str] = []
    for p in ports_list:
        for path in templates:
            urls.append(_build_rtsp_url(host, p, path, username, password))
    seen = set()
    uniq: List[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


def probe_common_rtsp(host: str, username: Optional[str], password: Optional[str], brand: str = "Unknown/Generic", ports: Optional[Iterable[int]] = None, max_to_try: int = 20, attempts: int = 8, delay: float = 0.1) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    candidates = generate_common_rtsp_urls(host, username, password, brand=brand, ports=ports)
    results: List[Dict[str, Any]] = []
    best_url: Optional[str] = None
    to_try = candidates[:max_to_try]
    logger.info("probe_common_rtsp: trying %s candidates host=%s brand=%s", len(to_try), host, brand)
    for url in to_try:
        masked = _mask_url(url)
        try:
            parts = urlsplit(url)
            if parts.hostname and parts.port:
                if not _tcp_reachable(parts.hostname, parts.port, timeout=1.5):
                    results.append({"url": url, "masked": masked, "ok": False, "fps": None, "size": None, "err": f"TCP not reachable {parts.hostname}:{parts.port}"})
                    logger.debug("probe_common_rtsp: skip %s (port unreachable)", masked)
                    continue
        except Exception:
            pass
        ok, fps, size, _jpeg, err = test_camera(url, attempts=attempts, delay=delay)
        results.append({"url": url, "masked": masked, "ok": ok, "fps": fps, "size": size, "err": err})
        if ok and best_url is None:
            best_url = url
            logger.info("probe_common_rtsp: found working %s", masked)
            break
    if best_url is None:
        logger.warning("probe_common_rtsp: no working RTSP URL found (tried=%s)", len(to_try))
    return best_url, results
