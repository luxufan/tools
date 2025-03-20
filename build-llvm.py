#!/usr/bin/env python3
"""
LLVM Build Automation Script
Author: Your Name
Description: Python-based build system for LLVM with runtime library support
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='LLVM Build Automation')

    # Core build options
    parser.add_argument('--source-dir', type=str, required=True,
                        help='Path to LLVM source directory (llvm-project/llvm)')
    parser.add_argument('--build-type', choices=['Debug', 'Release', 'RelWithDebInfo'],
                        default='Release', help='Build configuration type')
    parser.add_argument('--build-dir', type=str, default='build',
                        help='Build directory path (default: build)')
    parser.add_argument('--jobs', type=int, default=os.cpu_count(),
                        help=f'Number of parallel jobs (default: {os.cpu_count()})')

    # CMake feature flags
    parser.add_argument('--enable-stats', action='store_true',
                        help='Enable LLVM statistics tracking (-DLLVM_ENABLE_STATS=ON)')
    parser.add_argument('--export-compile-commands', action='store_true',
                        help='Generate compile_commands.json (-DCMAKE_EXPORT_COMPILE_COMMANDS=ON)')
    parser.add_argument('--enable-runtimes', type=str,
                        help='Enable LLVM runtimes (semicolon-separated, e.g., "libcxx;libcxxabi")')

    # LLVM-specific options
    parser.add_argument('--targets', type=str, default='all',
                        help='LLVM targets to build (semicolon-separated, e.g., "X86;ARM")')
    parser.add_argument('--components', type=str, default='clang;lld;clang-tools-extra',
                        help='LLVM components to build (semicolon-separated)')

    return parser.parse_args()

def configure_build(args, source_dir: Path, build_dir: Path):
    """Generate CMake build configuration"""
    cmake_args = [
        'cmake', '-G', 'Ninja',
        f'-DCMAKE_BUILD_TYPE={args.build_type}',
        f'-DLLVM_ENABLE_PROJECTS={args.components}',
        f'-DLLVM_TARGETS_TO_BUILD={args.targets}',
        f'-DLLVM_FORCE_ENABLE_STATS={"ON" if args.enable_stats else "OFF"}',
        f'-DCMAKE_EXPORT_COMPILE_COMMANDS={"ON" if args.export_compile_commands else "OFF"}',
    ]

    # Add runtime configuration if specified
    if args.enable_runtimes:
        cmake_args.append(f'-DLLVM_ENABLE_RUNTIMES={args.enable_runtimes}')

    cmake_args.append(str(source_dir))

    print(f"Configuring build in {build_dir}...")
    build_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(cmake_args, cwd=build_dir, check=True)

def build_project(build_dir: Path, jobs: int):
    """Compile LLVM project"""
    print(f"Building with {jobs} parallel jobs...")
    subprocess.run(['ninja', '-j', str(jobs)], cwd=build_dir, check=True)

def verify_build(build_dir: Path):
    """Check if build artifacts exist"""
    print("Verifying build artifacts...")
    clang_path = build_dir / 'bin' / 'clang'
    if not clang_path.exists():
        sys.exit(f"Verification failed: {clang_path} not found")

    if args.enable_runtimes:
        # Check for libc++ if enabled
        libcxx_header = build_dir / 'include' / 'c++' / 'v1' / 'vector'
        if 'libcxx' in (args.enable_runtimes or '') and not libcxx_header.exists():
            sys.exit(f"libc++ headers not found at {libcxx_header}")

    try:
        clang_version = subprocess.check_output(
            [str(clang_path), "--version"],
            stderr=subprocess.STDOUT
        ).decode().strip()
        print(f"Clang version:\n{clang_version}")
    except subprocess.CalledProcessError as e:
        sys.exit(f"Verification failed: {e}")

def main():
    """Main execution flow"""
    args = parse_arguments()

    # Convert paths to absolute Path objects
    source_dir = Path(args.source_dir).resolve()
    build_dir = Path(args.build_dir).resolve()

    if not source_dir.exists():
        sys.exit(f"Source directory {source_dir} does not exist")

    try:
        configure_build(args, source_dir, build_dir)
        build_project(build_dir, args.jobs)
        verify_build(build_dir)
        print(f"\nLLVM build completed successfully!")
        print(f"Artifacts located in: {build_dir}")
    except subprocess.CalledProcessError as e:
        sys.exit(f"Build failed with error: {e}")
    except Exception as e:
        sys.exit(f"Unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
