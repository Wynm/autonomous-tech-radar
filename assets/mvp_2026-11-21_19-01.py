#!/usr/bin/env python3
"""
Binary Hex-Dump Analyzer Micro-SaaS Core & Self-Test Engine
Standard Library Only (No external pip dependencies).
"""

import sys
import os
import tempfile
import json

class HexDumpAnalyzer:
    """Core analysis engine for binary hex dumps to detect patterns and structure."""
    
    def __init__(self, binary_data: bytes):
        self.data = binary_data
        
    def generate_hex_dump(self, bytes_per_line: int = 16) -> str:
        """Generates a standard hex dump string from binary data."""
        lines = []
        for i in range(0, len(self.data), bytes_per_line):
            chunk = self.data[i:i + bytes_per_line]
            hex_part = " ".join(f"{b:02x}" for b in chunk)
            ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
            lines.append(f"{i:08x}  {hex_part:<{bytes_per_line*3}}  |{ascii_part}|")
        return "\n".join(lines)
    
    def analyze_structure(self) -> dict:
        """Performs basic heuristic analysis on the binary structure."""
        total_size = len(self.data)
        null_bytes = self.data.count(b'\x00')
        
        # Detect potential magic numbers (file signatures)
        file_type = "Unknown/Custom"
        if self.data.startswith(b'\x7fELF'):
            file_type = "ELF Executable"
        elif self.data.startswith(b'MZ'):
            file_type = "PE Executable (DOS/Windows)"
        elif self.data.startswith(b'\x89PNG'):
            file_type = "PNG Image"
        elif total_size == 0:
            file_type = "Empty"

        return {
            "total_size_bytes": total_size,
            "detected_type": file_type,
            "null_byte_ratio": round(null_bytes / total_size, 4) if total_size > 0 else 0.0,
            "entropy_indicator": "High" if null_bytes < (total_size * 0.3) else "Low/Sparse"
        }

def run_self_test():
    """Executes a real internal verification test without touching system files."""
    print("[*] Running HexDumpAnalyzer Self-Test...")
    
    # Create a dummy ELF-like binary stream in memory for testing
    mock_binary = b'\x7fELF\x01\x01\x01\x00' + b'\x00' * 20 + b'HelloBinaryAI'
    
    analyzer = HexDumpAnalyzer(mock_binary)
    
    # Test 1: Hex Dump Generation
    dump = analyzer.generate_hex_dump(bytes_per_line=8)
    assert len(dump) > 0, "Hex dump generation failed."
    
    # Test 2: Structure Analysis
    analysis = analyzer.analyze_structure()
    assert analysis["detected_type"] == "ELF Executable", f"Expected ELF, got {analysis['detected_type']}"
    assert analysis["total_size_bytes"] == len(mock_binary), "Size mismatch."
    
    print("[+] Self-Test Passed Successfully!")
    print(json.dumps(analysis, indent=2))
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        success = run_self_test()
        sys.exit(0 if success else 1)
    else:
        print("Usage: python script.py --self-test")
        sys.exit(1)
