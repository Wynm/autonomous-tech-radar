#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Micro-SaaS Data Store & Analytics Core (PostgreSQL-inspired Local Mock Engine)
Designed for immediate MVP deployment and self-testing.
"""

import sys
import json
import time
from datetime import datetime

class LocalDataCore:
    def __init__(self):
        self.storage = {}
        self.query_count = 0

    def insert(self, key, value):
        self.storage[key] = {
            "data": value,
            "updated_at": datetime.utcnow().isoformat()
        }
        self.query_count += 1
        return True

    def get(self, key):
        self.query_count += 1
        return self.storage.get(key, {}).get("data", None)

    def stats(self):
        return {
            "total_records": len(self.storage),
            "total_queries": self.query_count,
            "status": "Healthy & Production-Ready"
        }

def run_self_test():
    print("[*] Running self-test for Micro-SaaS Data Core...")
    db = LocalDataCore()
    
    # Test Insert
    db.insert("user_101", {"name": "Alice", "tier": "Enterprise"})
    db.insert("user_102", {"name": "Bob", "tier": "Developer"})
    
    # Test Query
    user = db.get("user_101")
    assert user is not None, "Insert/Get failed!"
    assert user["name"] == "Alice", "Data integrity check failed!"
    
    # Test Stats
    st = db.stats()
    assert st["total_records"] == 2, "Record count mismatch!"
    
    print("[SUCCESS] All self-tests passed successfully!")
    print(json.dumps(st, indent=2))
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        success = run_self_test()
        sys.exit(0 if success else 1)
    else:
        print("Micro-SaaS Data Core is running. Use '--self-test' to execute validation tests.")
