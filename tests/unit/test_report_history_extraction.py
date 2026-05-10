import report_history_extraction


def test_extract_paper_titles_handles_both_parenthesis_styles():
    section = (
        "## A. Top Papers\n"
        "1) **Paper One**（English Title One）\n"
        "2) **Paper Two**(English Title Two)\n"
    )

    titles = report_history_extraction.extract_paper_titles(section)

    assert titles == [
        "Paper One（English Title One）",
        "Paper Two（English Title Two）",
    ]


def test_extract_project_names_filters_short_matches():
    section = "1) **Project Alpha**\n2) **AI**\n3) **Project Beta**"

    names = report_history_extraction.extract_project_names(section)

    assert names == ["Project Alpha", "Project Beta"]


def test_extract_news_urls_strips_trailing_parenthesis():
    section = "- 来源：https://example.com/news-item)\n- URL: https://example.com/news-two"

    urls = report_history_extraction.extract_news_urls(section)

    assert urls == [
        "https://example.com/news-item",
        "https://example.com/news-two",
    ]
