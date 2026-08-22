import json

path = 'c:/Users/Usuario/Downloads/ambisonic/Codigos/convert.ipynb'
with open(path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find the cell that defines load_sofa
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        if 'def load_sofa' in source:
            print(f'Found load_sofa at cell {i}')
            new_cell = {
                'cell_type': 'code',
                'execution_count': None,
                'metadata': {},
                'outputs': [],
                'source': [
                    '# =========================================================\n',
                    '# CARGA DE HRTF (INYECTADO)\n',
                    '# =========================================================\n',
                    'hrtf, pos = load_sofa(globals().get("hrtf_path", "hrtf.sofa"))\n',
                    'print("HRTF cargado correctamente.")'
                ]
            }
            nb['cells'].insert(i + 1, new_cell)
            with open(path, 'w', encoding='utf-8') as f2:
                json.dump(nb, f2, indent=1)
            print('Injected hrtf load code!')
            break
