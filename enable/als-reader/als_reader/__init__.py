"""als_reader — Custom Ableton Live Set parser for AI agent pipelines.

Usage:
    import als_reader

    project = als_reader.load("song.als")
    print(project.tempo)
    print(project.to_json())
"""
from __future__ import annotations

from pathlib import Path

from .models import ALSProject
from .parser import load_xml
from .extractors.transport import (
    extract_transport, extract_locators, extract_scale, extract_grooves,
)
from .extractors.tracks import extract_tracks, extract_master_track
from .extractors.scenes import extract_scenes


def load(file_path: str | Path) -> ALSProject:
    """Load an .als file and return a fully populated ALSProject.

    This is the primary public API. It decompresses the gzip'd XML,
    detects the Ableton version, and runs all extractors.

    Args:
        file_path: Path to the .als file.

    Returns:
        ALSProject with all extracted data.
    """
    root, version = load_xml(file_path)
    live_set = root.find("LiveSet")

    if live_set is None:
        # Still return a project with version info even if LiveSet is missing
        return ALSProject(
            file_path=str(file_path),
            version=version,
        )

    transport = extract_transport(live_set)
    locators = extract_locators(live_set)
    scale = extract_scale(live_set)
    grooves = extract_grooves(live_set)
    main_tracks, return_tracks = extract_tracks(live_set)
    master_track = extract_master_track(live_set)
    scenes = extract_scenes(live_set)

    return ALSProject(
        file_path=str(file_path),
        version=version,
        transport=transport,
        scale=scale,
        tracks=main_tracks,
        master_track=master_track,
        return_tracks=return_tracks,
        scenes=scenes,
        locators=locators,
        grooves=grooves,
    )


__all__ = ["load", "ALSProject"]
