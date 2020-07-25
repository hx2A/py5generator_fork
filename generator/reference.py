"""
Reference and Lookups
"""

PY5_SKIP_PARAM_TYPES = {
    'processing/core/PMatrix3D', 'processing/core/PMatrix2D',
    'processing/core/PMatrix', 'java/io/File', 'processing/core/PVector',
}

PY5_SKIP_RETURN_TYPES = PY5_SKIP_PARAM_TYPES | set()

JTYPE_CONVERSIONS = {
    'boolean': 'bool',
    'char': 'chr',
    'long': 'int',
    'java/lang/String': 'str',
    'java/lang/Object': 'Any',
    'processing/opengl/PShader': 'Py5Shader',
    'processing/core/PFont': 'Py5Font',
    'processing/core/PImage': 'Py5Image',
    'processing/core/PShape': 'Py5Shape',
    'processing/core/PSurface': 'Py5Surface',
    'processing/core/PGraphics': 'Py5Graphics',
}

PCONSTANT_OVERRIDES = {
    'WHITESPACE': r' \t\n\r\x0c\xa0',
    'ESC': r'\x1b',
    'RETURN': r'\r',
    'ENTER': r'\n',
    'DELETE': r'\x7f',
    'BACKSPACE': r'\x08',
    'TAB': r'\t',
}

EXTRA_DIR_NAMES = {
    'run_sketch', 'get_current_sketch', 'reset_py5',
    'JClass', 'Py5Exception', 'Sketch', 'Py5Font',
    'prune_tracebacks', 'set_stackprinter_style', 'create_font_file',
}
