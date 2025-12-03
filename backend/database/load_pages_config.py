import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict

# -----------------------------
# 1. Dataclass model
# -----------------------------
@dataclass
class MetaData:
    brand_default: str
    description: str
    tone_style: str
    main_objective: str

@dataclass
class ContentStrategy:
    core_questions: List[str]
    phone_request_template: str
    closing_strategy: str

@dataclass
class LogicRules:
    classification_rules: Dict[str, str]

@dataclass
class SystemSettings:
    call_me: str
    call_user: str

@dataclass
class FacebookSettings:
    FB_PAGE_ACCESS_TOKEN: str
    FB_VERIFY_TOKEN: str
    FB_PAGEID: str

@dataclass
class PageConfig:
    topic_id: str
    config_version: str
    meta_data: MetaData
    content_strategy: ContentStrategy
    logic_rules: LogicRules
    system_settings: SystemSettings
    facebook_settings: FacebookSettings  # <-- bổ sung

# -----------------------------
# 2. Hàm load từ một file JSON
# -----------------------------
def load_page_config(file_path: Path) -> PageConfig:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return PageConfig(
        topic_id=data.get("topic_id"),
        config_version=data.get("config_version"),
        meta_data=MetaData(**data.get("meta_data", {})),
        content_strategy=ContentStrategy(**data.get("content_strategy", {})),
        logic_rules=LogicRules(**data.get("logic_rules", {})),
        system_settings=SystemSettings(**data.get("system_settings", {})),
        facebook_settings=FacebookSettings(**data.get("facebook_settings", {}))  # <-- map FB
    )

# -----------------------------
# 3. Hàm load tất cả file JSON trong thư mục
# -----------------------------
def load_all_page_configs(folder_path: str) -> List[PageConfig]:
    folder = Path(folder_path)
    all_configs = []
    for file in folder.glob("*.json"):
        try:
            config = load_page_config(file)
            all_configs.append(config)
        except Exception as e:
            print(f"Failed to load {file}: {e}")
    return all_configs

def load_all_fb_tokens(folder_path: str) -> dict:
    from pathlib import Path
    import json
    tokens = {}
    for file in Path(folder_path).glob("*.json"):
        try:
            data = json.load(open(file, "r", encoding="utf-8"))
            fb = data.get("facebook_settings", {})
            page_id = fb.get("FB_PAGEID")
            token = fb.get("FB_PAGE_ACCESS_TOKEN")
            if page_id and token:
                tokens[page_id] = token
        except:
            continue
    return tokens

# -----------------------------
# 4. Ví dụ sử dụng
# -----------------------------
# if __name__ == "__main__":
#     folder_path = "config"  # folder chứa tất cả file JSON
#     pages = load_all_page_configs(folder_path)
#     print(f"Loaded {len(pages)} page configs.")
#     for page in pages:
#         print(page.topic_id, page.meta_data.brand_default)
#         print("FB PAGEID:", page.facebook_settings.FB_PAGEID)
