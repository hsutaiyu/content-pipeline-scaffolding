"""Thin Notion API wrapper. All Notion I/O lives here; stages never touch HTTP."""

import os

import requests

BASE = "https://api.notion.com/v1"
VERSION = "2022-06-28"


# --- property value helpers (build the {"type": ...} dicts Notion expects) ---

def title(s: str) -> dict:
    return {"title": [{"text": {"content": s}}]}


def text(s: str) -> dict:
    return {"rich_text": [{"text": {"content": s}}]}


def select(name: str) -> dict:
    return {"select": {"name": name}}


def multi_select(names: list[str]) -> dict:
    return {"multi_select": [{"name": n} for n in names]}


def date(iso: str) -> dict:
    return {"date": {"start": iso}}


def relation(ids: list[str]) -> dict:
    return {"relation": [{"id": i} for i in ids]}


def paragraph(s: str) -> dict:
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": [{"text": {"content": s}}]}}


class Notion:
    def __init__(self, token: str | None = None):
        self.token = token or os.environ.get("NOTION_API_KEY", "")
        if not self.token:
            raise RuntimeError("NOTION_API_KEY is required")

    def _request(self, method: str, path: str, payload: dict | None = None) -> dict:
        kwargs: dict = {"timeout": 60}
        if method == "GET":
            kwargs["params"] = payload
        else:
            kwargs["json"] = payload
        resp = requests.request(
            method,
            f"{BASE}{path}",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": VERSION,
            },
            **kwargs,
        )
        if resp.status_code != 200:
            raise RuntimeError(
                f"Notion {method} {path} failed: {resp.status_code} {resp.text[:500]}"
            )
        return resp.json()

    def create_database(self, parent_page_id: str, name: str, properties: dict) -> str:
        data = self._request("POST", "/databases", {
            "parent": {"page_id": parent_page_id},
            "title": [{"text": {"content": name}}],
            "properties": properties,
        })
        return data["id"]

    def query(self, db_id: str, filter: dict | None = None,
              sorts: list | None = None) -> list[dict]:
        payload: dict = {}
        if filter:
            payload["filter"] = filter
        if sorts:
            payload["sorts"] = sorts
        results: list[dict] = []
        while True:
            data = self._request("POST", f"/databases/{db_id}/query", payload)
            results.extend(data["results"])
            if not data.get("has_more"):
                return results
            payload["start_cursor"] = data["next_cursor"]

    def create_page(self, parent: dict, properties: dict,
                    children: list | None = None) -> str:
        payload: dict = {"parent": parent, "properties": properties}
        if children:
            payload["children"] = children
        return self._request("POST", "/pages", payload)["id"]

    def update_properties(self, page_id: str, properties: dict) -> None:
        self._request("PATCH", f"/pages/{page_id}", {"properties": properties})

    def append_blocks(self, page_id: str, blocks: list) -> None:
        self._request("PATCH", f"/blocks/{page_id}/children", {"children": blocks})

    def get_page_markdown(self, page_id: str) -> str:
        blocks: list[dict] = []
        params: dict = {}
        while True:
            data = self._request("GET", f"/blocks/{page_id}/children", params)
            blocks.extend(data["results"])
            if not data.get("has_more"):
                break
            params = {"start_cursor": data["next_cursor"]}
        return "\n".join(_block_to_md(b) for b in blocks if _block_to_md(b))


def _plain(block: dict) -> str:
    kind = block.get("type", "")
    return "".join(t.get("plain_text", "")
                   for t in block.get(kind, {}).get("rich_text", []))


def _block_to_md(block: dict) -> str:
    kind = block.get("type", "")
    text = _plain(block)
    if not text and kind != "divider":
        return ""
    if kind == "heading_1":
        return f"# {text}"
    if kind == "heading_2":
        return f"## {text}"
    if kind == "heading_3":
        return f"### {text}"
    if kind == "bulleted_list_item":
        return f"- {text}"
    if kind == "numbered_list_item":
        return f"1. {text}"
    if kind == "to_do":
        return f"- [ ] {text}"
    if kind == "quote":
        return f"> {text}"
    if kind == "divider":
        return "---"
    return text
