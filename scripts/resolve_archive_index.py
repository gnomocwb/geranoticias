import subprocess
import json
from pathlib import Path

def resolve():
    out_head = subprocess.check_output(['git', 'show', ':2:public/data/archive_index.json'], encoding='utf-8')
    out_remote = subprocess.check_output(['git', 'show', ':3:public/data/archive_index.json'], encoding='utf-8')

    head_items = json.loads(out_head)
    remote_items = json.loads(out_remote)

    items_by_id = {}
    for item in remote_items:
        items_by_id[item['id']] = item

    for item in head_items:
        items_by_id[item['id']] = item

    merged = list(items_by_id.values())
    merged.sort(key=lambda x: (x.get('date', ''), x.get('time', '')), reverse=True)

    public_dir = Path('public')
    valid_merged = []
    for item in merged:
        file_path = public_dir / item.get('file', '')
        if file_path.exists():
            valid_merged.append(item)
        else:
            print(f"File not found on disk, skipping: {item.get('file')}")

    with open('public/data/archive_index.json', 'w', encoding='utf-8') as f:
        json.dump(valid_merged, f, ensure_ascii=False, indent=2)

    print(f"Sucesso: {len(valid_merged)} edições indexadas sem conflito.")

if __name__ == '__main__':
    resolve()
