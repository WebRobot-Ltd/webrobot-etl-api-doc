#!/usr/bin/env python3
"""
Script per rimuovere tutti gli endpoint legacy dalla documentazione OpenAPI.
"""

import yaml
from pathlib import Path

def main():
    openapi_file = Path(__file__).parent.parent / 'openapi.yaml'
    
    print(f"📖 Leggendo {openapi_file}...")
    with open(openapi_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    paths = data.get('paths', {})
    removed_count = 0
    
    # Trova e rimuovi tutti gli endpoint legacy
    legacy_paths = [path for path in paths.keys() if 'datasets-legacy' in path]
    
    print(f"🔍 Trovati {len(legacy_paths)} endpoint legacy da rimuovere...")
    
    for path in legacy_paths:
        print(f"  - Rimuovendo: {path}")
        del paths[path]
        removed_count += 1
    
    print(f"✨ Rimossi {removed_count} endpoint legacy...")
    
    # Salva
    print(f"💾 Salvando in {openapi_file}...")
    with open(openapi_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)
    
    print("✅ Completato!")

if __name__ == '__main__':
    main()

