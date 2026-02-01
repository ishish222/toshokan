from pathlib import Path
from pkgutil import extend_path

# Allow src/ layout while keeping this package shim in place.
__path__ = extend_path(__path__, __name__)
_src_pkg = Path(__file__).resolve().parents[1] / "src" / __name__
if _src_pkg.exists():
    __path__.append(str(_src_pkg))
