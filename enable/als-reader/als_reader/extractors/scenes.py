"""Extract session view scenes."""
from __future__ import annotations

import logging
from xml.etree.ElementTree import Element

from ..models import Scene, FollowAction
from ._xml_helpers import find, find_all, attr_int, value_str, value_int, value_float, value_bool

logger = logging.getLogger(__name__)


def _extract_scene_follow_action(scene_el: Element) -> FollowAction | None:
    fa_el = find(scene_el, "FollowAction")
    if fa_el is None:
        return None
    return FollowAction(
        follow_time=value_float(fa_el, "FollowTime"),
        is_linked=value_bool(fa_el, "IsLinked"),
        enabled=value_bool(fa_el, "FollowActionEnabled"),
    )


def extract_scenes(live_set: Element) -> list[Scene]:
    """Extract scenes from LiveSet."""
    scenes_el = find(live_set, "Scenes")
    if scenes_el is None:
        return []

    result = []
    for scene_el in find_all(scenes_el, "Scene"):
        tempo = value_float(scene_el, "Tempo")
        # Ableton uses -1 to mean "no scene tempo"
        if tempo is not None and tempo < 0:
            tempo = None

        ts_id = value_int(scene_el, "TimeSignatureId")
        if ts_id is not None and ts_id < 0:
            ts_id = None

        result.append(Scene(
            id=attr_int(scene_el, "Id"),
            name=value_str(scene_el, "Name"),
            color=value_int(scene_el, "Color"),
            tempo=tempo,
            time_signature_id=ts_id,
            follow_action=_extract_scene_follow_action(scene_el),
        ))

    return result
