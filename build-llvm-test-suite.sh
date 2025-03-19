#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Configuration
LLVM_DIR="$HOME/llvm/build-release"  # Update this path to your LLVM installation
TEST_SUITE_DIR="$HOME/llvm-test-suite"  # Update this path to your test suite
SPEC2006_ROOT="$HOME/spec2006"
CMAKE_CONFIG="$TEST_SUITE_DIR/cmake/caches/ReleaseLTO.cmake"
BUILD_DIR="$TEST_SUITE_DIR/build-compare"
NUM_JOBS=$(nproc)  # Use all available CPU cores


# Create build directory
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Configure build using CMake
cmake -G "Ninja" \
    -DLLVM_DIR="$LLVM_DIR/lib/cmake/llvm" \
    -DTEST_SUITE_SUBDIRS="External" \
    -DCMAKE_C_COMPILER="$LLVM_DIR/bin/clang" \
    -DCMAKE_CXX_COMPILER="$LLVM_DIR/bin/clang++" \
    -DTEST_SUITE_SPEC2006_ROOT=$SPEC2006_ROOT \
    -DTEST_SUITE_COLLECT_STATS=ON \
    -DTEST_SUITE_USE_PERF=ON \
    -C"$CMAKE_CONFIG" \
    -DTEST_SUITE_EXTRA_LIT_MODULES="perf"  \
    "$TEST_SUITE_DIR"

# Build the test suite
cmake --build . -- -j"$NUM_JOBS"

# Optionally, run tests
echo "Running LLVM Test Suite..."
$LLVM_DIR/bin/llvm-lit -v -j 56 -o results.json .

echo "LLVM Test Suite build and testing completed!"

