"""Backward-compatible facade for report generation.

The implementation lives in llm_client (LLM API calls) and report_utils
(path building, saving, link validation, network detection).  This module
re-exports the public names so that existing callers continue to work
without import changes.
"""

# Re-export from new modules
from report_utils import (  # noqa: F401
    build_output_path,
    check_domestic_network,
    save_report,
    validate_and_fix_arxiv_links,
)
from llm_client import generate_content  # noqa: F401
