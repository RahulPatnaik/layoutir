#!/bin/bash
# Local installation test script for LayoutIR

set -e  # Exit on error

echo "🧪 LayoutIR - Local Installation Test"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Activate conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate PDF

# Navigate to project
cd /home/rahul/Desktop/CHUNK-MY-PDF

echo -e "${BLUE}📦 Step 1: Cleaning old builds${NC}"
rm -rf dist/ build/ src/*.egg-info 2>/dev/null || true
echo "✓ Cleaned"
echo ""

echo -e "${BLUE}📦 Step 2: Building package${NC}"
python -m build
echo "✓ Built successfully"
echo ""

echo -e "${BLUE}📋 Build artifacts:${NC}"
ls -lh dist/
echo ""

echo -e "${BLUE}💾 Step 3: Installing package${NC}"
pip uninstall -y layoutir 2>/dev/null || true
pip install dist/layoutir-1.0.0-py3-none-any.whl
echo "✓ Installed"
echo ""

echo -e "${BLUE}✅ Step 4: Running tests${NC}"
echo ""

# Test 1: Version
echo -n "Test 1: Version check... "
VERSION=$(python -c "from layoutir import __version__; print(__version__)")
if [ "$VERSION" == "1.0.0" ]; then
    echo -e "${GREEN}✓ PASSED${NC} (v$VERSION)"
else
    echo -e "${RED}✗ FAILED${NC}"
    exit 1
fi

# Test 2: Imports
echo -n "Test 2: Import check... "
python -c "
from layoutir import Document, Block, BlockType, Chunk, Manifest
from layoutir.pipeline import Pipeline
from layoutir.adapters import DoclingAdapter
from layoutir.chunking import SemanticSectionChunker
from layoutir.exporters import MarkdownExporter, TextExporter, ParquetExporter
" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASSED${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    exit 1
fi

# Test 3: CLI
echo -n "Test 3: CLI check... "
layoutir --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASSED${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    exit 1
fi

# Test 4: CLI location
echo -n "Test 4: CLI installed at... "
CLI_PATH=$(which layoutir)
echo -e "${GREEN}$CLI_PATH${NC}"

# Test 5: Package metadata
echo -n "Test 5: Package metadata... "
AUTHOR=$(pip show layoutir | grep "Author:" | cut -d' ' -f2-)
if [ "$AUTHOR" == "Rahul Patnaik" ]; then
    echo -e "${GREEN}✓ PASSED${NC} ($AUTHOR)"
else
    echo -e "${RED}✗ FAILED${NC}"
    exit 1
fi

# Test 6: Full pipeline test
echo -n "Test 6: Full pipeline test... "
python test_pipeline.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASSED${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 All tests passed!${NC}"
echo -e "${GREEN}✅ Package is ready for PyPI upload${NC}"
echo ""
echo "Next steps:"
echo "  1. Create PyPI account at https://pypi.org/account/register/"
echo "  2. Create API token"
echo "  3. Upload: python -m twine upload dist/*"
