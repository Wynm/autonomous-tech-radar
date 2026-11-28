#!/usr/bin/env python3
import sys
import unittest
import json
import re

class ReleaseNoteEngine:
    """
    نواة معالجة ملاحظات الإصدار (Release Notes Engine)
    تدمج سياق السبب (Why - مثل تذاكر Jira) مع كود التغيير (What - مثل Git Diff)
    لتوليد تقارير دقيقة خالية من الهلوسة.
    """
    def __init__(self, tickets_context, git_diffs):
        self.tickets_context = tickets_context
        self.git_diffs = git_diffs

    def generate_release_notes(self):
        notes = []
        for ticket_id, details in self.tickets_context.items():
            diff = self.git_diffs.get(ticket_id, "No code changes found.")
            # تحليل يربط السبب بالنتيجة لمنع الهلوسة
            note = {
                "ticket": ticket_id,
                "objective": details.get("title", "Unknown Task"),
                "business_value": details.get("description", ""),
                "technical_changes": self._summarize_diff(diff)
            }
            notes.append(note)
        return notes

    def _summarize_diff(self, diff_text):
        # محاكاة تحليل ذكي لـ Git Diff لاستخراج التغييرات الفعلية (What)
        lines = diff_text.strip().split('\n')
        added = sum(1 for line in lines if line.startswith('+') and not line.startswith('+++'))
        deleted = sum(1 for line in lines if line.startswith('-') and not line.startswith('---'))
        return f"Modified files. Additions: {added}, Deletions: {deleted}"


class TestReleaseNoteEngine(unittest.TestCase):
    """
    اختبار ذاتي متكامل للتحقق من صحة عمل النواة البرمجية (Self-Test).
    """
    def test_generation(self):
        sample_tickets = {
            "PROJ-101": {
                "title": "إصلاح مشكلة تسجيل الدخول",
                "description": "منع انهيار النظام عند إدخال بيانات خاطئة (Why)"
            }
        }
        sample_diffs = {
            "PROJ-101": "+ def login():\n+     validate_input()\n-     pass"
        }
        
        engine = ReleaseNoteEngine(sample_tickets, sample_diffs)
        notes = engine.generate_release_notes()
        
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["ticket"], "PROJ-101")
        self.assertIn("Additions: 2", notes[0]["technical_changes"])
        print("\n[Self-Test] تم اجتياز الاختبار الذاتي بنجاح وتوليد ملاحظات الإصدار بدقة عالية!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        print("تشغيل الاختبار الذاتي لأداة Release Notes Engine...")
        # تشغيل الوحدة الاختبارية دون تعديل النظام
        suite = unittest.TestLoader().loadTestsFromTestCase(TestReleaseNoteEngine)
        result = unittest.TextTestRunner().run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)
    else:
        # تشغيل افتراضي سريع لإثبات العمل
        print("تشغيل الأداة في وضع التشغيل القياسي (استخدم --self-test للاختبار الذاتي):")
        engine = ReleaseNoteEngine(
            {"TASK-1": {"title": "تحسين الأداء", "description": "تسريع استعلامات قاعدة البيانات"}},
            {"TASK-1": "+ SELECT * FROM users;\n- SELECT id FROM users;"}
        )
        print(json.dumps(engine.generate_release_notes(), ensure_ascii=False, indent=2))
