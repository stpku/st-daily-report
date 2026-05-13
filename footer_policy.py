"""Footer selection policy for WeChat daily report rendering."""

from __future__ import annotations

import os
import random
import re
from dataclasses import dataclass
from glob import glob


ADMIN_CONTACT_LINK = "https://mp.weixin.qq.com/s/H79SAUA1GB0AcKUD6DSDdQ"
RISK_ENV = "ST_DAILYREPORT_FOOTER_RISK_MODE"


@dataclass(frozen=True)
class FooterSelection:
    """Selected footer file plus policy metadata."""

    path: str
    variant: str
    risk_mode: str


class FooterPolicy:
    """Choose a low-risk footer variant with mild editorial variation."""

    def __init__(self, config_dir: str, rng: random.Random | None = None):
        self.config_dir = config_dir
        self.rng = rng or random.Random()
        self.last_selection: FooterSelection | None = None

    def available_variants(self) -> list[str]:
        pattern = os.path.join(self.config_dir, "footer_intro*.md")
        return sorted(path for path in glob(pattern) if os.path.isfile(path))

    def choose(self, risk_mode: str | None = None) -> FooterSelection | None:
        risk = (risk_mode or os.environ.get(RISK_ENV, "") or "normal").strip().lower()
        variants = [path for path in self.available_variants() if self._is_safe_footer(path)]
        if not variants:
            self.last_selection = None
            return None

        if risk in {"low_cta", "cooldown", "quiet"}:
            quiet = [path for path in variants if path.endswith("footer_intro_v3.md")]
            candidates = quiet or variants
        else:
            candidates = variants

        chosen = self.rng.choice(candidates)
        self.last_selection = FooterSelection(
            path=chosen,
            variant=os.path.basename(chosen),
            risk_mode=risk,
        )
        return self.last_selection

    def _is_safe_footer(self, path: str) -> bool:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            return False

        if "![" in content:
            return False
        if re.search(r"(扫码|二维码|添加微信|个人微信|私域|回复领取)", content):
            return False

        links = re.findall(r"\]\((https?://[^)]+)\)", content)
        if not links:
            return False
        return all(link == ADMIN_CONTACT_LINK for link in links)
