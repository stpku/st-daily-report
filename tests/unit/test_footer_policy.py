import random

from footer_policy import ADMIN_CONTACT_LINK, FooterPolicy


def test_footer_policy_accepts_only_safe_link_variants(tmp_path):
    safe = tmp_path / "footer_intro.md"
    safe.write_text(f"[查看管理员联系方式]({ADMIN_CONTACT_LINK})", encoding="utf-8")
    unsafe_qr = tmp_path / "footer_intro_v2.md"
    unsafe_qr.write_text(f"![二维码](x.jpg)\n[查看管理员联系方式]({ADMIN_CONTACT_LINK})", encoding="utf-8")
    unsafe_link = tmp_path / "footer_intro_v3.md"
    unsafe_link.write_text("[其他链接](https://example.com)", encoding="utf-8")

    selection = FooterPolicy(str(tmp_path), rng=random.Random(1)).choose()

    assert selection is not None
    assert selection.path == str(safe)


def test_footer_policy_quiet_mode_prefers_v3_when_safe(tmp_path):
    base = tmp_path / "footer_intro.md"
    base.write_text(f"[查看管理员联系方式]({ADMIN_CONTACT_LINK})", encoding="utf-8")
    quiet = tmp_path / "footer_intro_v3.md"
    quiet.write_text(f"[查看管理员联系方式]({ADMIN_CONTACT_LINK})", encoding="utf-8")

    selection = FooterPolicy(str(tmp_path), rng=random.Random(1)).choose("quiet")

    assert selection is not None
    assert selection.variant == "footer_intro_v3.md"
