import report_prompting


def test_get_language_settings_returns_expected_english_defaults():
    settings = report_prompting.get_language_settings("en")

    assert settings["lang_instruction"] == "English"
    assert settings["keyword_label"] == "Keywords"


def test_build_history_constraints_limits_paper_list_to_ten():
    history_constraint, papers_constraint = report_prompting.build_history_constraints(
        recent_projects=["Project A", "Project B"],
        recent_papers=[f"Paper {index}" for index in range(12)],
    )

    assert "Project A, Project B" in history_constraint
    assert "Paper 0" in papers_constraint
    assert "Paper 9" in papers_constraint
    assert "Paper 10" not in papers_constraint


def test_build_user_prompt_adds_enforcement_for_english():
    prompt = report_prompting.build_user_prompt("English", "en")

    assert "Generate a English GeoAI daily report" in prompt
    assert "Do not use the phrase OPC机会." in prompt
    assert "You MUST use the EXACT papers" in prompt


def test_build_system_prompt_includes_new_section_names_and_scope_reference():
    settings = report_prompting.get_language_settings("zh")

    prompt = report_prompting.build_system_prompt(
        date_str="2026-05-10",
        settings=settings,
        news_context="news-context",
        papers_context="papers-context",
        history_constraint="history-constraint",
        papers_constraint="papers-constraint",
    )

    assert settings["section_c_title"] in prompt
    assert settings["section_d_title"] in prompt
    assert settings["mainline_label"] in prompt
    assert settings["scope_line"] in prompt
    assert "news-context" in prompt
    assert "papers-context" in prompt
