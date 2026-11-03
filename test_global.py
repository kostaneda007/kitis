"""Compatibility entry point; the v9 single-scale suite supersedes card assertions."""
from pathlib import Path
exec(compile(Path(__file__).with_name('test_single_scale.py').read_text(), 'test_single_scale.py', 'exec'))
