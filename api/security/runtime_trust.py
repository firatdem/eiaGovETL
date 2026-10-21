"""Apply verified build-time installer updates and reject compromised trust roots."""
import hashlib
import importlib
import os
from pathlib import Path
import re
import ssl
import subprocess
import sys
import zipfile

BLOCKED = {
    "86a1ecba089c4a8d3bbe2734c612ba341d813e043cf9e8a862cd5c57a36bbe6b",
    "d7a7a0fb5d7e2731d771e9484ebcdef71d5f0c3e0a2948782bc83ee0ea699ef4",
}
WHEELS = {
    "pip": ("26.2.2", "fd7f4dfa8190e014013b9f08f3e973f4e4c26ffd179a204895533a7254813a70"),
    "setuptools": ("83.0.0", "29b23c360f22f414dc7336bb39178cc7bcbf6021ed2733cde173f09dba19abb3"),
}

def check_bundle(data):
    certificates = re.findall(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", data, re.S)
    if not certificates:
        raise RuntimeError("Empty certificate bundle")
    roots = {hashlib.sha256(ssl.PEM_cert_to_DER_cert(c)).hexdigest() for c in certificates}
    if roots & BLOCKED:
        raise RuntimeError("Affected certificate remains trusted")
    return len(roots)

def verify():
    import pip._vendor.certifi
    import certifi
    check_bundle(Path(ssl.get_default_verify_paths().cafile).read_text())
    check_bundle(Path(pip._vendor.certifi.where()).read_text())
    check_bundle(Path(certifi.where()).read_text())
    import ensurepip
    bundled = Path(ensurepip.__file__).parent / "_bundled"
    for package, (version, digest) in WHEELS.items():
        wheel = bundled / f"{package}-{version}-py3-none-any.whl"
        if hashlib.sha256(wheel.read_bytes()).hexdigest() != digest:
            raise RuntimeError("Unexpected ensurepip wheel")
        if len(list(bundled.glob(f"{package}-*.whl"))) != 1:
            raise RuntimeError("Obsolete installer wheel remains")
    with zipfile.ZipFile(bundled / "pip-26.2.2-py3-none-any.whl") as z:
        check_bundle(z.read("pip/_vendor/certifi/cacert.pem").decode())

def bootstrap():
    if sys.platform != "linux" or os.geteuid() != 0 or str(Path(__file__)) != "/opt/security/runtime_trust.py":
        raise RuntimeError("This bootstrap is only for the Docker build")
    import ensurepip
    source = Path(ensurepip.__file__)
    text = source.read_text()
    bundled = source.parent / "_bundled"
    wheels = []
    for package, (version, digest) in WHEELS.items():
        wheel = Path("/tmp") / f"{package}-{version}-py3-none-any.whl"
        payload = wheel.read_bytes()
        if hashlib.sha256(payload).hexdigest() != digest:
            raise RuntimeError("Installer wheel checksum mismatch")
        pattern = rf'(?m)^_{package.upper()}_VERSION = "[^"]+"$'
        text, count = re.subn(pattern, f'_{package.upper()}_VERSION = "{version}"', text)
        if count != 1:
            raise RuntimeError("Unexpected ensurepip source layout")
        for old in bundled.glob(f"{package}-*.whl"):
            old.unlink()
        (bundled / wheel.name).write_bytes(payload)
        wheels.append(str(wheel))
    source.write_text(text)
    subprocess.run([sys.executable, "-m", "pip", "install", "--no-index", "--no-deps", *wheels], check=True)
    for wheel in wheels:
        Path(wheel).unlink()

if __name__ == "__main__":
    if sys.argv[1:] == ["bootstrap"]:
        bootstrap()
    elif sys.argv[1:] == ["verify"]:
        verify()
    else:
        raise SystemExit("Expected bootstrap or verify")
