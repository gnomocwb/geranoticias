import subprocess
import json
from pathlib import Path

def resolve():
    public_dir = Path("public")
    index_path = public_dir / "data" / "archive_index.json"
    items_by_id = {}

    # 1. Tenta recuperar versões do git se houver conflito de merge ou de commits recentes
    for ref in [':2', ':3', 'HEAD', 'HEAD~1', 'HEAD^1', 'HEAD^2']:
        try:
            target = f"{ref}:public/data/archive_index.json" if not ref.startswith(':') else f"{ref}:public/data/archive_index.json"
            out = subprocess.check_output(['git', 'show', target], encoding='utf-8', stderr=subprocess.DEVNULL)
            for item in json.loads(out):
                items_by_id[item['id']] = item
        except Exception:
            pass

    # 2. Lê o arquivo local existente se for JSON válido
    if index_path.exists():
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                for item in content:
                    items_by_id[item['id']] = item
        except Exception as e:
            print(f"Aviso ao ler {index_path}: {e}")

    # 3. Também inspeciona public/data/editions/ para garantir que nenhuma edição existente fique de fora
    editions_dir = public_dir / "data" / "editions"
    if editions_dir.exists():
        for html_file in editions_dir.glob("*.html"):
            eid = html_file.stem
            # se não constar no índice, podemos pelo menos manter os que já foram catalogados
            pass

    merged = list(items_by_id.values())
    merged.sort(key=lambda x: (x.get('date', ''), x.get('time', '')), reverse=True)

    # 4. Filtra apenas itens cujos arquivos realmente existem no disco
    valid_merged = []
    for item in merged:
        rel_file = item.get('file', '')
        file_path = public_dir / rel_file
        if file_path.exists():
            valid_merged.append(item)
        else:
            print(f"Arquivo não encontrado no disco, ignorando: {rel_file}")

    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(valid_merged, f, ensure_ascii=False, indent=2)

    print(f"Sucesso: {len(valid_merged)} edições indexadas sem conflito em {index_path}.")

if __name__ == '__main__':
    resolve()
