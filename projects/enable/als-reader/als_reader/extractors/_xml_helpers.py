"""Safe XML navigation helpers — never raise on missing elements."""
from __future__ import annotations

import logging
from typing import Optional
from xml.etree.ElementTree import Element

logger = logging.getLogger(__name__)


def find(el: Optional[Element], path: str) -> Optional[Element]:
    """Find a child element, returning None if not found."""
    if el is None:
        return None
    return el.find(path)


def find_all(el: Optional[Element], path: str) -> list[Element]:
    """Find all matching children, returning [] if parent is None."""
    if el is None:
        return []
    return el.findall(path)


def attr(el: Optional[Element], key: str = "Value") -> Optional[str]:
    """Get an attribute from an element, returning None if missing."""
    if el is None:
        return None
    return el.attrib.get(key)


def attr_float(el: Optional[Element], key: str = "Value") -> Optional[float]:
    """Get a float attribute."""
    v = attr(el, key)
    if v is None:
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        logger.warning("Could not parse float from %s=%s", key, v)
        return None


def attr_int(el: Optional[Element], key: str = "Value") -> Optional[int]:
    """Get an int attribute."""
    v = attr(el, key)
    if v is None:
        return None
    try:
        return int(v)
    except (ValueError, TypeError):
        logger.warning("Could not parse int from %s=%s", key, v)
        return None


def attr_bool(el: Optional[Element], key: str = "Value") -> Optional[bool]:
    """Get a bool attribute (Ableton uses 'true'/'false' strings)."""
    v = attr(el, key)
    if v is None:
        return None
    return v.lower() == "true"


def value_float(parent: Optional[Element], child_tag: str) -> Optional[float]:
    """Shortcut: parent.find(child_tag).attrib['Value'] as float."""
    return attr_float(find(parent, child_tag))


def value_int(parent: Optional[Element], child_tag: str) -> Optional[int]:
    """Shortcut: parent.find(child_tag).attrib['Value'] as int."""
    return attr_int(find(parent, child_tag))


def value_str(parent: Optional[Element], child_tag: str) -> Optional[str]:
    """Shortcut: parent.find(child_tag).attrib['Value'] as str."""
    return attr(find(parent, child_tag))


def value_bool(parent: Optional[Element], child_tag: str) -> Optional[bool]:
    """Shortcut: parent.find(child_tag).attrib['Value'] as bool."""
    return attr_bool(find(parent, child_tag))


def manual_value(parent: Optional[Element], param_tag: str) -> Optional[float]:
    """Get the Manual value from a parameter element (e.g., Volume/Manual)."""
    param_el = find(parent, param_tag)
    if param_el is None:
        return None
    return attr_float(find(param_el, "Manual"))
