import json
import os

def optimize_notebook(path):
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    new_cells = []
    for cell in nb['cells']:
        if cell['cell_type'] != 'code':
            new_cells.append(cell)
            continue
            
        source = "".join(cell['source'])
        
        # Skip installation cells completely
        if '!pip install' in source or '!apt-get' in source or '!curl' in source or '!wget' in source:
            continue
            
        # Modify hrtf load code in convert
        if 'hrtf, pos = load_sofa("hrtf.sofa")' in source:
            # We assume hrtf_path is passed as parameter, fallback to hrtf.sofa
            source = source.replace('hrtf, pos = load_sofa("hrtf.sofa")', 'hrtf, pos = load_sofa(globals().get("hrtf_path", "hrtf.sofa"))')
            cell['source'] = [line + '\n' for line in source.split('\n')]
            # Remove trailing newline from last element
            if cell['source']:
                cell['source'][-1] = cell['source'][-1].rstrip('\n')
        
        # Modify SOFA_DEFAULT_PATH in demo
        if 'SOFA_DEFAULT_PATH = "hrtf.sofa"' in source:
            source = source.replace('SOFA_DEFAULT_PATH = "hrtf.sofa"', 'SOFA_DEFAULT_PATH = globals().get("hrtf_path", "hrtf.sofa")')
            cell['source'] = [line + '\n' for line in source.split('\n')]
            if cell['source']:
                cell['source'][-1] = cell['source'][-1].rstrip('\n')
                
        new_cells.append(cell)
        
    nb['cells'] = new_cells
    
    # Inject hrtf_path into parameters cell if not there
    for cell in nb['cells']:
        if cell['cell_type'] == 'code' and 'tags' in cell.get('metadata', {}) and 'parameters' in cell['metadata']['tags']:
            source = "".join(cell['source'])
            if 'hrtf_path =' not in source:
                cell['source'].append('\nhrtf_path = ""')
            break
            
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)

print("Optimizing convert.ipynb")
optimize_notebook("c:/Users/Usuario/Downloads/ambisonic/Codigos/convert.ipynb")
print("Optimizing demo.ipynb")
optimize_notebook("c:/Users/Usuario/Downloads/ambisonic/Codigos/demo.ipynb")
print("Done")
