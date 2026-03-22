"""Extract automation envelopes from tracks."""
from __future__ import annotations

import logging
from xml.etree.ElementTree import Element

from ..models import AutomationEnvelope, AutomationPoint
from ._xml_helpers import find, find_all, attr_int, attr_float, value_int

logger = logging.getLogger(__name__)


def extract_automation_envelopes(device_chain_el: Element | None) -> list[AutomationEnvelope]:
    """Extract track-level automation envelopes from a DeviceChain."""
    if device_chain_el is None:
        return []

    ae_el = find(device_chain_el, "AutomationEnvelopes")
    if ae_el is None:
        return []

    envelopes_el = find(ae_el, "Envelopes")
    if envelopes_el is None:
        return []

    result = []
    for env_el in find_all(envelopes_el, "AutomationEnvelope"):
        env_id = attr_int(env_el, "Id")

        target = find(env_el, "EnvelopeTarget")
        pointee_id = value_int(target, "PointeeId") if target is not None else None

        points = []
        automation = find(env_el, "Automation")
        events = find(automation, "Events") if automation is not None else None
        if events is not None:
            for evt in find_all(events, "AutomationEvent"):
                points.append(AutomationPoint(
                    time=attr_float(evt, "Time"),
                    value=attr_float(evt, "Value"),
                ))

        result.append(AutomationEnvelope(
            id=env_id,
            pointee_id=pointee_id,
            points=points,
        ))

    return result
