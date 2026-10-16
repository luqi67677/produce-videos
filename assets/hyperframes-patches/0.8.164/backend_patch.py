"""Hyperframes 0.8.164: pure full-track range-cut endpoint; never writes runtime."""
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
MARKER = '// pv-sync-cut-1: pure range edit; persistence is owned by Studio CAS/history.'

def patch(source: str) -> str:
    if MARKER in source:
        return source
    anchor = 'async function foldAtomicCutFile(c, file, absPath, before, writer) {'
    route_anchor = '  api.post("/projects/:id/file-mutations/split-batch", async (c) => {'
    if source.count(anchor) != 1 or source.count(route_anchor) != 1:
        raise ValueError('Unsupported Hyperframes backend: expected 0.8.164 anchors')
    source = source.replace(anchor, (HERE / 'range_cut.js').read_text() + '\n' + anchor, 1)
    return source.replace(route_anchor, (HERE / 'range_cut_routes.js').read_text() + '\n' + route_anchor, 1) + '\nexport { pvRangeCutPreviewHtml };\n'

def test_module(source: str, dist: Path) -> str:
    result = patch(source)
    result = re.sub(r'((?:from\s+|import\s*\()\")\./([^\"]+)(\")', lambda m: m[1] + (dist / m[2]).as_uri() + m[3], result)
    return result + '\nexport { parseSourceDocument, fileContentVersion };\n'

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--test-module', action='store_true')
    args = parser.parse_args()
    source = args.source.read_text()
    args.output.write_text(test_module(source, args.source.parent.resolve()) if args.test_module else patch(source))
