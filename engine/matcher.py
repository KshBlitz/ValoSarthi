"""
Matching engine.
Builds path from 4 inputs, checks if lineup exists, returns data.
"""

import os
import json
from dataclasses import dataclass
from typing import Optional

from engine.state import LINEUPS_DIR, site_to_folder


@dataclass
class Lineup:
    throw:      str          # "normal" or "jump"
    stand_path: str          # absolute path to stand.png (may not exist)
    aim_path:   str          # absolute path to aim.gif   (may not exist)
    folder:     str          # the lineup folder path

    @property
    def has_stand(self) -> bool:
        return os.path.isfile(self.stand_path)

    @property
    def has_aim(self) -> bool:
        return os.path.isfile(self.aim_path)


def match_lineup(
    map_name: str,
    agent: str,
    spike_site: str,
    agent_position: str,
) -> Optional[Lineup]:
    """
    Exact folder-match lookup.
    Path: lineups/{map}/{agent}/{spike_site}/{agent_position}/
    Returns Lineup or None.
    """
    folder = os.path.join(
        LINEUPS_DIR,
        map_name.lower(),
        agent.lower(),
        site_to_folder(spike_site),
        agent_position.lower(),         # "b_main" or "mid"
    )

    if not os.path.isdir(folder):
        return None

    meta_path = os.path.join(folder, "meta.json")
    throw = "normal"
    if os.path.isfile(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)
        throw = meta.get("throw", "normal").lower()

    return Lineup(
        throw=throw,
        stand_path=os.path.join(folder, "stand.png"),
        aim_path=os.path.join(folder, "aim.gif"),
        folder=folder,
    )
