#!/usr/bin/env python3
"""公開申請（プルリクエスト）の説明文を作る。

標準入力: 変更されたファイルの一覧（1行1ファイル）
環境変数: PREVIEW_URL（確認用ページのURL）、ISSUE_NUMBER（任意）
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]


def read_title(path: str) -> str:
    try:
        text = (ROOT / path).read_text(encoding="utf-8")
    except OSError:
        return ""
    match = re.search(r"^title:\s*(.+?)\s*$", text, re.M)
    return match.group(1).strip("'\"") if match else ""


def describe(changed: list[str], preview_url: str) -> tuple[list[str], list[str]]:
    """(変更内容の説明, 確認するページのURL) を返す。"""
    items, pages = [], []
    for raw in changed:
        path = raw.strip()
        p = PurePosixPath(path)
        if p.parts[:1] == ("content",) and len(p.parts) == 3 and p.suffix == ".md":
            kind = p.parts[1]
            title = read_title(path) or p.stem
            if kind == "news":
                items.append(f"お知らせ「{title}」")
                pages.append(f"- お知らせ「{title}」: {preview_url}news/{p.stem}.html")
            elif kind == "jobs":
                items.append(f"求人「{title}」")
                pages.append(f"- 求人「{title}」: {preview_url}jobs/{p.stem}.html")
        elif path == "site.yml":
            items.append("会社情報・トップページの文章や画像の設定")
        elif p.parts[:1] == ("images",):
            items.append(f"画像（{p.name}）")
        elif p.parts[:1] == ("templates",):
            items.append(f"ページの文言（{p.name}）")
        else:
            items.append(f"その他（{path}）")
    pages.append(f"- トップページ: {preview_url}")
    return items, pages


def build_body(changed: list[str], preview_url: str, issue_no: str) -> str:
    items, pages = describe(changed, preview_url)
    lines = ["## 変更した内容", ""]
    lines += [f"- {item}" for item in items]
    lines += ["", "## 確認用ページ", "", "1〜2分後に、次のページで見た目を確認できます（まだ一般には公開されていません）。", ""]
    lines += pages
    lines += [
        "",
        "## 公開のしかた",
        "",
        "1. 上の確認用ページで内容を確認します",
        "2. 直したいところがあれば、このページの一番下のコメント欄に `@claude ○○を直してください` と書いて送信します",
        "3. 問題がなければ、下の **「Merge pull request」→「Confirm merge」** を押します。2〜3分後に本番サイトに反映されます",
        "",
        "公開しない場合は、「Close pull request」を押してください。",
    ]
    if issue_no:
        lines += ["", f"Closes #{issue_no}"]
    return "\n".join(lines) + "\n"


def main() -> int:
    changed = [line for line in sys.stdin.read().splitlines() if line.strip()]
    preview_url = os.environ.get("PREVIEW_URL", "").rstrip("/") + "/"
    print(build_body(changed, preview_url, os.environ.get("ISSUE_NUMBER", "")), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
