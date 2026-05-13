import os
import json
import requests
import re
import time
import sys
import html
import path_utils
from footer_policy import FooterPolicy

# WeChat Official Account CSS Styles (module-level constant)
STYLES = {
    'h1': 'font-size: 22px; font-weight: bold; text-align: center; margin: 18px 0 24px; color: #182433; line-height: 1.45;',
    'h2': 'font-size: 18px; font-weight: bold; color: #1f2d3d; border-left: 5px solid #2f80ed; padding-left: 12px; margin: 34px 0 6px 0; line-height: 1.4;',
    'h3': 'font-size: 16px; font-weight: bold; color: #1f2d3d; margin: 25px 0 10px 0;',
    'p': 'font-size: 16px; line-height: 1.75; color: #3f3f3f; margin: 15px 0; text-align: justify;',
    'ul': 'margin: 10px 0 15px 0; padding-left: 0; list-style: none;',
    'li': 'font-size: 15px; line-height: 1.75; color: #3f3f3f; margin-bottom: 8px; text-align: left; padding-left: 0;',
    'blockquote': 'border-left: 4px solid #e0e0e0; padding-left: 12px; color: #666; margin: 15px 0; font-size: 15px;',
    'code': 'font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace; font-size: 14px; background-color: #f6f8fa; padding: 2px 4px; border-radius: 4px; color: #c7254e;',
    'pre': 'background-color: #f6f8fa; padding: 16px; overflow-x: auto; border-radius: 6px; margin: 16px 0; font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace; font-size: 14px; line-height: 1.45;',
    'a': 'color: #576b95; text-decoration: none; word-break: break-all;',
    'strong': 'font-weight: bold; color: #333;',
    'hr': 'border: 0; border-top: 1px solid #eee; margin: 30px 0;',
    'insight': 'color: #e67e22; font-weight: bold;',
    'paper_title': 'font-size: 17px; font-weight: bold; color: #2c3e50; display: block; margin-top: 25px; margin-bottom: 10px; line-height: 1.5;',
    'paper_meta': 'font-size: 13px; color: #6f7f8f; margin: 7px 0 12px 0; padding: 8px 10px; background-color: #f8fafc; border-radius: 4px; display: block; word-break: break-all; line-height: 1.65;',
    'judgment': 'font-size: 15px; line-height: 1.75; color: #243447; margin: 8px 0; padding: 10px 12px; background-color: #f7fbff; border-left: 4px solid #2f80ed; border-radius: 4px; text-align: left;',
    'keywords': 'font-size: 14px; line-height: 1.7; color: #576b95; margin: 12px 0 22px 0; padding: 8px 10px; background-color: #f6f8fa; border-radius: 4px; text-align: left;',
    'mainline': 'font-size: 15px; line-height: 1.75; color: #1f2d3d; margin: 8px 0 10px 0; padding: 12px 14px; background-color: #fffaf2; border-left: 4px solid #f2994a; border-radius: 4px; text-align: left;',
    'section_hint': 'font-size: 13px; color: #8a97a6; margin: 0 0 14px 17px; line-height: 1.6; text-align: left;',
    'item_title': 'font-size: 16px; font-weight: bold; color: #243447; line-height: 1.55; margin: 18px 0 4px 0; text-align: left;',
    'item_original': 'font-size: 13px; color: #7a8794; line-height: 1.55; margin-top: 4px; font-weight: normal; word-break: break-word;',
}

SECTION_HINTS = {
    "今日判断": "先看主线，再扫三条判断",
    "Today's Read": "Start with the main signal, then scan three judgments",
    "A) Top Papers（精选 3-5 篇）": "精选论文｜方法、数据与评测趋势",
    "A) Top Papers (3-5 selected papers)": "Selected papers | methods, data, evaluation",
    "A) Top Papers": "Selected papers | methods, data, evaluation",
    "B) Industry News（产业动态，精选 3-5 条）": "产业动态｜只保留高相关信号",
    "B) Industry News": "Industry signals | direct relevance first",
    "C) 工具 / 数据 / 开源更新": "工具与数据｜有价值才展开",
    "C) Tools / Data / Open Source Updates": "Tools and data | expand only when valuable",
    "D) 问题线索 / 创新机会": "从今日材料提炼可讨论的问题",
    "D) Problem Leads / Innovation Opportunities": "Problem leads distilled from today's materials",
}


class WeChatSync:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self._load_config()
        self.app_id = self.config.get('wx_app_id')
        self.secret = self.config.get('wx_app_secret')
        self.token = None
        self.token_expiry = 0
        self.last_footer_selection = None

    def _load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def get_access_token(self):
        if self.token and time.time() < self.token_expiry:
            return self.token

        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.secret}"
        resp = requests.get(url, timeout=30)
        data = resp.json()

        if 'access_token' in data:
            self.token = data['access_token']
            # Refresh 200s before expiry
            self.token_expiry = time.time() + data['expires_in'] - 200
            return self.token
        else:
            raise Exception(f"Failed to get access token: {data}")

    def get_cover_media_id(self):
        if 'wx_cover_media_id' in self.config:
            return self.config['wx_cover_media_id']

        token = self.get_access_token()
        # Use permanent material for cover images
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"

        base_dir = os.path.dirname(self.config_path)
        cover_path = os.path.join(base_dir, 'cover.jpg')

        if not os.path.exists(cover_path):
            print("Cover image not found. Downloading placeholder...")
            try:
                img_url = "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1080&auto=format&fit=crop" # Tech/Space theme
                img_resp = requests.get(img_url, timeout=10)
                if img_resp.status_code == 200:
                    with open(cover_path, 'wb') as f:
                        f.write(img_resp.content)
                else:
                    raise Exception("Failed to download image")
            except Exception as e:
                print(f"Error getting placeholder: {e}")
                return None

        with open(cover_path, 'rb') as f:
            files = {'media': f}
            resp = requests.post(url, files=files, timeout=30)
            data = resp.json()

        if 'media_id' in data:
            self.config['wx_cover_media_id'] = data['media_id']
            self._save_config()
            return data['media_id']
        else:
            print(f"Failed to upload cover: {data}")
            return None

    def upload_content_image(self, image_path):
        if not os.path.exists(image_path):
            print(f"Footer image not found: {image_path}")
            return None

        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"

        with open(image_path, 'rb') as f:
            resp = requests.post(url, files={'media': f}, timeout=30)
            data = resp.json()

        if 'url' in data:
            return data['url']

        print(f"Failed to upload footer image: {data}")
        return None

    def md_to_html(self, md_content):
        # Pre-process content to handle custom markers
        md_content = self._preprocess_content(md_content)

        # Block-level parsing
        return self._block_parse(md_content)

    def _preprocess_content(self, content):
        content = re.sub(r"Date: \d{4}-\d{2}-\d{2}", "", content)
        content = re.sub(r"> 注：以上为.*", "", content)
        content = re.sub(r"注：以上为.*", "", content)
        # Use regex to add ** markers without breaking line structure
        content = re.sub(r'^Scope:', '**Scope:**', content, flags=re.MULTILINE)
        content = re.sub(r'^Key Message:', '**Key Message:**', content, flags=re.MULTILINE)
        return content

    def _get_list_prefix(self, current_section, list_index):
        prefix = ""
        if "Open Source" in current_section or "开源" in current_section:
            list_index += 1
            prefix = f"{list_index}) "
        return prefix, list_index

    def _is_judgment_section(self, current_section):
        return current_section in {"今日判断", "Today's Read"}

    def _render_judgment_item(self, content):
        return (
            f'<p style="{STYLES["judgment"]}">'
            '<span style="font-weight: bold; color: #2f80ed; margin-right: 6px;">•</span>'
            f'{self._process_inline(content)}</p>'
        )

    def _render_keyword_line(self, text):
        match = re.match(r"^(今日关键词|Keywords)\s*[:：]\s*(.+)$", text, flags=re.IGNORECASE)
        if not match:
            return ""
        label = html.escape(match.group(1), quote=False)
        value = self._process_inline(match.group(2).strip())
        return (
            f'<p style="{STYLES["keywords"]}">'
            f'<strong style="color: #2f80ed;">{label}：</strong>{value}</p>'
        )

    def _render_mainline_line(self, text):
        match = re.match(r"^(今日主线|Main Thread)\s*[:：]\s*(.+)$", text, flags=re.IGNORECASE)
        if not match:
            return ""
        label = html.escape(match.group(1), quote=False)
        value = self._process_inline(match.group(2).strip())
        return (
            f'<p style="{STYLES["mainline"]}">'
            f'<strong style="color: #c96f17;">{label}：</strong>{value}</p>'
        )

    def _render_list_item(self, content, prefix="", current_section=""):
        if self._is_judgment_section(current_section):
            return self._render_judgment_item(content)

        match = re.match(r'^\*\*(.*?)\*\*(.*)', content)
        if match:
            title_text = match.group(1).strip()
            rest_text = match.group(2).strip()
            if rest_text.startswith(':') or rest_text.startswith('：'):
                rest_text = rest_text[1:].strip()

            # Escape HTML in user-controlled content
            safe_title_text = html.escape(title_text, quote=False)
            safe_prefix = html.escape(prefix, quote=False)

            item_html = (
                '<p style="font-size: 15px; line-height: 1.75; color: #3f3f3f; '
                'margin: 4px 0 8px 0; text-align: left;">'
                f'<span style="margin-right: 8px; color: #333;">•</span>'
                f'<strong style="color: #2c3e50;">{safe_prefix}{safe_title_text}</strong></p>'
            )
            if rest_text:
                item_html += (
                    '<p style="font-size: 14px; line-height: 1.75; color: #555; '
                    'margin: 0 0 8px 24px; text-align: left;">'
                    f'{self._process_inline(rest_text)}</p>'
                )
            return item_html

        return (
            '<p style="font-size: 15px; line-height: 1.75; color: #3f3f3f; '
            'margin: 4px 0 8px 0; text-align: left;">'
            f'<span style="margin-right: 8px; color: #333;">•</span>{prefix}'
            f'{self._process_inline(content)}</p>'
        )

    def _render_heading_line(self, line):
        if line.startswith('# '):
            return f'<h1 style="{STYLES["h1"]}">{self._process_inline(line[2:])}</h1>', None, None
        if line.startswith('## '):
            current_section = line[3:]
            hint = SECTION_HINTS.get(current_section)
            hint_html = (
                f'<p style="{STYLES["section_hint"]}">{self._process_inline(hint)}</p>'
                if hint else ""
            )
            return (
                f'<h2 style="{STYLES["h2"]}">{self._process_inline(current_section)}</h2>{hint_html}',
                current_section,
                0,
            )
        if line.startswith('### '):
            return f'<h3 style="{STYLES["h3"]}">{self._process_inline(line[4:])}</h3>', None, None
        return "", None, None

    def _render_blockquote_line(self, line):
        content = self._process_inline(line[2:])
        return f'<blockquote style="{STYLES["blockquote"]}">{content}</blockquote>'

    def _render_paper_title_line(self, line, current_section=""):
        full_line = line.replace('**', '')
        match = re.match(r'^(\d+)\)\s*(.+)$', full_line.strip())
        if not match:
            return f'<div style="{STYLES["paper_title"]}">{self._process_inline(full_line)}</div>'

        index = match.group(1)
        title = match.group(2).strip()
        original = ""
        paren_match = re.match(r'^(.+?)（([^（）]{8,260})）$', title)
        if not paren_match:
            paren_match = re.match(r'^(.+?)\(([^()]{8,260})\)$', title)
        if paren_match:
            title = paren_match.group(1).strip()
            original = paren_match.group(2).strip()

        label = "原题" if current_section.startswith("A)") else "原标题"
        original_html = ""
        if original:
            original_html = (
                f'<div style="{STYLES["item_original"]}">'
                f'{label}：{self._process_inline(original)}</div>'
            )

        return (
            f'<div style="{STYLES["item_title"]}">'
            f'<span style="display: inline-block; min-width: 22px; color: #2f80ed;">{index})</span>'
            f'{self._process_inline(title)}{original_html}</div>'
        )

    def _render_paragraph_line(self, line):
        return f'<p style="{STYLES["p"]}">{self._process_inline(line)}</p>'

    def _block_parse(self, text):
        lines = text.split('\n')
        output = []
        in_list = False
        in_code_block = False
        code_content = []

        list_index = 0
        current_section = ""

        # Wrapper div
        output.append(f'<div style="font-family: -apple-system, BlinkMacSystemFont, \'PingFang SC\', \'Microsoft YaHei\', sans-serif; font-size: 16px; line-height: 1.75; color: #333333; text-align: justify;">')

        for line in lines:
            line_stripped = line.strip()

            # --- Code Block Handling ---
            if line_stripped.startswith('```'):
                if in_code_block:
                    # End code block
                    code_html = '\n'.join(code_content)
                    output.append(f'<pre style="{STYLES["pre"]}"><code style="background-color: transparent; color: inherit;">{code_html}</code></pre>')
                    in_code_block = False
                    code_content = []
                else:
                    # Start code block
                    in_code_block = True
                continue

            if in_code_block:
                safe_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                code_content.append(safe_line)
                continue

            # --- Normal Line Handling ---
            if not line_stripped:
                # Close list if open
                if in_list:
                    in_list = False
                continue

            # Skip lines that are just a bullet point with no text (artifacts from footer or bad parsing)
            if re.match(r'^[-*+]\s*$', line_stripped):
                continue

            # Skip standalone - (hyphen) lines that create empty list items
            if line_stripped == '-':
                continue

            meta_html = self._render_meta_line(line_stripped)
            if meta_html:
                output.append(meta_html)
                continue

            signal_html = self._render_signal_line(line_stripped)
            if signal_html:
                output.append(signal_html)
                continue

            mainline_html = self._render_mainline_line(line_stripped)
            if mainline_html:
                output.append(mainline_html)
                continue

            keyword_html = self._render_keyword_line(line_stripped)
            if keyword_html:
                output.append(keyword_html)
                continue

    # Special case: **Key Message:** should not trigger list mode
            if '**Key Message:**' in line:
                output.append(self._render_paragraph_line(line))
                continue

            # Skip empty lines after headers to avoid creating empty list items
            if not line_stripped and not in_list:
                continue

            heading_html, next_section, next_list_index = self._render_heading_line(line)
            if heading_html:
                if next_section is not None:
                    current_section = next_section
                if next_list_index is not None:
                    list_index = next_list_index
                output.append(heading_html)
                continue

            # Horizontal Rule
            if line.startswith('---'):
                output.append(f'<hr style="{STYLES["hr"]}"/>')
                continue

            # Lists (use <p> with manual bullet for WeChat compatibility)
            if line.startswith('- ') or line.startswith('* '):
                if not in_list:
                    in_list = True

                content = line[2:].strip()
                prefix, list_index = self._get_list_prefix(current_section, list_index)
                output.append(self._render_list_item(content, prefix, current_section))
                continue

            # Blockquotes
            if line.startswith('> '):
                if in_list:
                    in_list = False
                output.append(self._render_blockquote_line(line))
                continue

            # Paper Title: 1) **Title**
            if re.match(r'^\d+\)\s*\*\*(.*?)\*\*', line):
                match = re.match(r'^\d+\)\s*\*\*(.*?)\*\*(.*)', line)
                if match:
                    output.append(self._render_paper_title_line(line, current_section))
                    continue

            # Paragraphs
            if in_list:
                in_list = False
            output.append(self._render_paragraph_line(line))

        if in_list:
            pass  # no </ul> needed with <p> based lists

        output.append('</div>')
        return '\n'.join(output)

    def _strip_bullet_prefix(self, text):
        return re.sub(r'^[-*+]\s+', '', text.strip())

    def _render_meta_line(self, text):
        clean = self._strip_bullet_prefix(text)
        match = re.match(
            r'^(Link|Source|URL|原文|来源|GitHub|项目地址|论文链接)\s*[:：]\s*(.+)$',
            clean,
            flags=re.IGNORECASE
        )
        if not match:
            return ""

        label = match.group(1)
        value = self._process_inline(match.group(2).strip())
        return (
            f'<div style="{STYLES["paper_meta"]}">'
            f'<strong style="color: #576b95;">{label}：</strong>{value}'
            f'</div>'
        )

    def _render_signal_line(self, text):
        clean = self._strip_bullet_prefix(text)
        clean = re.sub(r'^\*\*(One-line Insight|Impact|Why it matters|Description)\s*[:：]\*\*', r'\1:', clean, flags=re.IGNORECASE)
        match = re.match(
            r'^(One-line Insight|Impact|Why it matters|Description|为什么重要|影响|为什么关注|灵感)\s*[:：]\s*(.+)$',
            clean,
            flags=re.IGNORECASE
        )
        if not match:
            return ""

        label = match.group(1)
        value = self._process_inline(match.group(2).strip())
        return (
            f'<p style="{STYLES["p"]}">'
            f'<span style="{STYLES["insight"]}">{label}：</span>{value}'
            f'</p>'
        )

    def _process_inline(self, text):
        """Process inline markdown → HTML. Parse tokens first, escape per-part."""

        # Phase 1: Extract markdown tokens and replace with placeholders
        tokens = []

        def _store_token(replacement):
            idx = len(tokens)
            tokens.append(replacement)
            return f'\x00TOKEN{idx}\x00'

        # 1. Extract links [text](url) first (before other processing)
        def _replace_link(m):
            link_text = m.group(1)
            url = m.group(2)
            # Validate URL protocol — only allow http/https
            if not re.match(r'^https?://', url, re.IGNORECASE):
                url = '#'
            safe_url = html.escape(url, quote=True)
            safe_text = html.escape(link_text, quote=False)
            return _store_token(f'<a href="{safe_url}" style="{STYLES["a"]}">{safe_text}</a>')
        text = re.sub(r'\[(.*?)\]\(((?:[^()]*|\([^()]*\))*)\)', _replace_link, text)

        # 2. Extract bold **text**
        def _replace_bold(m):
            safe_inner = html.escape(m.group(1), quote=False)
            return _store_token(f'<strong style="{STYLES["strong"]}">{safe_inner}</strong>')
        text = re.sub(r'\*\*(.+?)\*\*', _replace_bold, text)

        # 3. Extract code `text`
        def _replace_code(m):
            safe_inner = html.escape(m.group(1), quote=False)
            return _store_token(f'<code style="{STYLES["code"]}">{safe_inner}</code>')
        text = re.sub(r'`(.*?)`', _replace_code, text)

        # 4. Extract italic *text*
        def _replace_italic(m):
            safe_inner = html.escape(m.group(1), quote=False)
            return _store_token(f'<em>{safe_inner}</em>')
        text = re.sub(r'(?<!\w)\*([^*]+?)\*(?!\w)', _replace_italic, text)

        # 5. Extract bare URLs from unescaped text BEFORE escaping
        def _replace_bare_url(m):
            bare_url = m.group(1)
            safe_url = html.escape(bare_url, quote=True)
            safe_display = html.escape(bare_url, quote=False)
            return _store_token(f'<a href="{safe_url}" style="{STYLES["a"]}">{safe_display}</a>')
        text = re.sub(r'(?<!\()(https?://[^\s<\)]+)', _replace_bare_url, text)

        # Phase 2: Split by placeholders, escape remaining text
        parts = re.split(r'(\x00TOKEN\d+\x00)', text)
        result_parts = []
        for part in parts:
            token_match = re.match(r'\x00TOKEN(\d+)\x00', part)
            if token_match:
                result_parts.append(tokens[int(token_match.group(1))])
            else:
                escaped = html.escape(part, quote=False)
                result_parts.append(escaped)

        return ''.join(result_parts)

    def _process_footer(self, md_content, base_dir=None):
        lines = md_content.split('\n')
        html_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue

            image_match = re.match(r'^!\[(.*?)\]\((.*?)\)$', line)
            if image_match:
                alt = image_match.group(1).strip()
                src = image_match.group(2).strip()
                if not re.match(r'^https?://', src, flags=re.IGNORECASE):
                    image_path = src if os.path.isabs(src) else os.path.join(base_dir or os.path.dirname(self.config_path), src)
                    uploaded_src = self.upload_content_image(image_path)
                    if not uploaded_src:
                        continue
                    src = uploaded_src

                html_lines.append(
                    '<div style="text-align: center; margin: 18px 0 4px 0;">'
                    f'<img src="{src}" alt="{alt}" style="width: 220px; max-width: 72%; height: auto; border-radius: 6px; display: inline-block;" />'
                    '</div>'
                )
                continue

            # Convert lists to simple paragraphs
            if line.startswith('- ') or line.startswith('* '):
                content = line[2:].strip()
                html_lines.append(f'<p style="{STYLES["p"]}">{self._process_inline(content)}</p>')
            # Headers
            elif line.startswith('## '):
                content = line[3:].strip()
                html_lines.append(f'<h2 style="{STYLES["h2"]}">{self._process_inline(content)}</h2>')
            elif line.startswith('### '):
                content = line[4:].strip()
                html_lines.append(f'<h3 style="{STYLES["h3"]}">{self._process_inline(content)}</h3>')
            # Normal text
            else:
                html_lines.append(f'<p style="{STYLES["p"]}">{self._process_inline(line)}</p>')

        return '\n'.join(html_lines)

    def verify_html(self, html_content):
        print("Verifying HTML content...")

        warnings = []

        clean_for_check = re.sub(r'>\*\*<', '', html_content)
        clean_for_check = re.sub(r'</\*\*', '', clean_for_check)
        clean_for_check = re.sub(r'style="[^"]*\*"', '', clean_for_check)
        if re.search(r'[^*]\*\*[^*]', clean_for_check):
            warnings.append("Found potential unrendered bold markers (**)")

        # Check for * (italic) not replaced
        # Tricky because * is used in CSS, regex, etc. But HTML shouldn't have loose * usually.
        # We look for * surrounded by spaces or words, but not inside tags.
        # This is a heuristic.
        clean_text = re.sub(r'<[^>]+>', '', html_content) # Strip tags
        if re.search(r'(?<!\*)\*(?!\*)', clean_text):
             # Filter out common footnote chars or math if any, but alert for now
             pass

        if warnings:
            print("WARNING: HTML Verification Issues found:")
            for w in warnings:
                print(f"- {w}")
        else:
            print("HTML Verification Passed: No obvious markdown artifacts found.")

    def _build_title(self, file_path: str) -> str:
        basename = os.path.basename(file_path)
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', basename)
        if date_match:
            date_str = date_match.group(0)
        else:
            date_str = time.strftime('%Y-%m-%d')
        return f"燕园时空｜GeoAI & World Model 前沿日报 {date_str}"

    def _build_gitee_link_html(self, file_path: str) -> str:
        try:
            rel_path = os.path.relpath(file_path, start=os.path.dirname(os.path.dirname(self.config_path)))
            rel_path = rel_path.replace(os.sep, '/')
            gitee_url = f"https://gitee.com/stpku/st-daily-report/blob/master/{rel_path}"
            return (
                '<div style="text-align: left; margin-bottom: 20px;">'
                '<span style="font-size: 14px; color: #576b95; background-color: #f2f2f2; '
                'padding: 10px; border-radius: 4px; display: inline-block;">原文链接：<br>'
                f'<span style="font-size: 12px; color: #7f8c8d; word-break: break-all;">{gitee_url}</span>'
                '</span></div>'
            )
        except Exception as e:
            print(f"Error generating Gitee link: {e}")
            return ""

    def _build_footer_html(self) -> str:
        config_dir = os.path.dirname(self.config_path)
        selection = FooterPolicy(config_dir).choose()
        self.last_footer_selection = selection
        footer_path = selection.path if selection else None
        if not footer_path or not os.path.exists(footer_path):
            return ""
        with open(footer_path, 'r', encoding='utf-8') as f:
            footer_md = f.read()
        footer_content = self._process_footer(footer_md, base_dir=os.path.dirname(footer_path))
        return (
            '<section style="margin-top: 40px; padding: 18px 18px 16px 18px; '
            'background-color: #f3f7fb; border: 1px solid #c9d8ea; '
            'border-left: 5px solid #2f80ed; border-radius: 6px;">'
            f'{footer_content}</section>'
        )

    @staticmethod
    def _extract_digest(content: str) -> str:
        digest = "Daily updates on GeoAI and World Models."
        if "摘要" in content:
            digest_match = re.search(r'摘要[：|:]\s*(.*)', content)
            if digest_match:
                digest = digest_match.group(1).strip()
        if len(digest) > 50:
            digest = digest[:50] + "..."
        return digest

    def _create_draft(self, token: str, title: str, html_content: str, cover_id: str, digest: str) -> bool:
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
        payload = {
            "articles": [
                {
                    "title": title,
                    "author": "燕园时空客",
                    "content": html_content,
                    "thumb_media_id": cover_id,
                    "digest": digest
                }
            ]
        }
        payload_json = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        print(f"Draft title: {title}")
        resp = requests.post(url, data=payload_json, headers={'Content-Type': 'application/json; charset=utf-8'}, timeout=30)
        res_data = resp.json()

        if 'media_id' in res_data:
            print(f"Successfully created draft: {res_data['media_id']}")
            return True
        else:
            print(f"Failed to create draft: {res_data}")
            if res_data.get('errcode') == 40007:
                print("Invalid cover media ID. Clearing from config.")
                if 'wx_cover_media_id' in self.config:
                    del self.config['wx_cover_media_id']
                    self._save_config()
            return False

    def sync(self, file_path):
        if not self.app_id or not self.secret:
            print("Skipping WeChat Sync: Credentials missing.")
            return False

        token = self.get_access_token()
        cover_id = self.get_cover_media_id()

        if not cover_id:
            print("Skipping WeChat Sync: Could not get cover image.")
            return False

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        title = self._build_title(file_path)
        link_html = self._build_gitee_link_html(file_path)
        footer_html = self._build_footer_html()
        digest = self._extract_digest(content)

        html_content = self.md_to_html(content)
        final_html = link_html + html_content + footer_html

        self.verify_html(final_html)
        return self._create_draft(token, title, final_html, cover_id, digest)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        config_path = path_utils.resolve_path(
            path_utils.config_path('config_secret.json'),
            os.path.join(os.path.dirname(__file__), 'config_secret.json'),
        )
        syncer = WeChatSync(config_path)
        syncer.sync(sys.argv[1])
    else:
        print("Usage: python wechat_sync.py <markdown_file_path>")
