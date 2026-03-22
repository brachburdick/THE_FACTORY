"""Core parser: gzip decompression + XML parsing + version detection."""
from __future__ import annotations

import gzip
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

from .models import VersionInfo

logger = logging.getLogger(__name__)


def decompress_als(file_path: str | Path) -> bytes:
    """Decompress a .als file (gzip) and return raw XML bytes."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"ALS file not found: {path}")

    with gzip.open(path, "rb") as f:
        return f.read()


def parse_xml(xml_bytes: bytes) -> ET.Element:
    """Parse XML bytes into an ElementTree root element."""
    return ET.fromstring(xml_bytes)


def detect_version(root: ET.Element) -> VersionInfo:
    """Extract version info from the root <Ableton> element attributes."""
    return VersionInfo(
        creator=root.attrib.get("Creator"),
        major_version=root.attrib.get("MajorVersion"),
        minor_version=root.attrib.get("MinorVersion"),
        schema_change_count=root.attrib.get("SchemaChangeCount"),
    )


def load_xml(file_path: str | Path) -> tuple[ET.Element, VersionInfo]:
    """Load an .als file and return (root element, version info).

    This is the primary entry point for the parser layer.
    """
    xml_bytes = decompress_als(file_path)
    root = parse_xml(xml_bytes)
    version = detect_version(root)
    logger.info("Parsed %s — %s", file_path, version.creator or "unknown version")
    return root, version
