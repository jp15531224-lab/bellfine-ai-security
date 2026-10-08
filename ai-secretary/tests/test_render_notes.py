import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import render_notes as rn  # noqa: E402

SAMPLE = json.loads((HERE.parent / "samples" / "sample_extraction.json").read_text(encoding="utf-8"))


class TestHelpers(unittest.TestCase):
    def test_plaud_utc_to_jst(self):
        self.assertEqual(rn.plaud_start_to_jst("2026-10-07T02:36:59"), "2026-10-07T11:36:59+09:00")
        self.assertEqual(rn.plaud_start_to_jst("2026-10-07T16:55:58"), "2026-10-08T01:55:58+09:00")

    def test_mask(self):
        m = rn.mask("連絡先 090-1234-5678 / 09012345678 / a.b@example.com / 口座番号 1234567")
        self.assertNotIn("1234-5678", m)
        self.assertNotIn("09012345678", m)
        self.assertNotIn("example.com", m)
        self.assertNotIn("1234567", m)

    def test_mask_keeps_money_and_dates(self):
        self.assertEqual(rn.mask("処分費3,000円 2026-10-07 10t"), "処分費3,000円 2026-10-07 10t")

    def test_person_key_strips_honorific_and_bad_chars(self):
        self.assertEqual(rn.person_key("山田太郎さん"), "山田太郎")
        self.assertEqual(rn.person_key("林専務"), "林")
        self.assertEqual(rn.person_key("a/b[c]#"), "abc")


class TestValidate(unittest.TestCase):
    def test_sample_ok(self):
        self.assertEqual(rn.validate(SAMPLE), [])

    def test_confirmed_schedule_needs_transcript(self):
        d = copy.deepcopy(SAMPLE)
        d["source"]["basis"] = "要約のみ"
        self.assertTrue(any("要約のみ" in e for e in rn.validate(d)))

    def test_confirmed_schedule_needs_evidence_and_time(self):
        d = copy.deepcopy(SAMPLE)
        d["schedules"][0].pop("evidence")
        d["schedules"][0].pop("start")
        errs = rn.validate(d)
        self.assertTrue(any("evidence" in e for e in errs))
        self.assertTrue(any("start" in e for e in errs))

    def test_relative_due_rejected(self):
        d = copy.deepcopy(SAMPLE)
        d["todos"][0]["due"] = "来週"
        self.assertTrue(any("YYYY-MM-DD" in e for e in rn.validate(d)))

    def test_naive_time_rejected(self):
        d = copy.deepcopy(SAMPLE)
        d["source"]["recorded_at"] = "2026-10-01T15:00:00"
        self.assertTrue(rn.validate(d))


class TestRender(unittest.TestCase):
    def setUp(self):
        self.files = rn.render_all([SAMPLE], "2026-10-08T12:00+09:00")
        self.by = {(f["folder"], f["filename"]): f for f in self.files}

    def test_all_create_if_absent(self):
        self.assertTrue(all(f["mode"] == "create_if_absent" for f in self.files))

    def test_minutes_filename_has_source_id(self):
        names = [f["filename"] for f in self.files if f["folder"] == "議事録"]
        self.assertEqual(names, ["2026-10-01_1500_（サンプル）山田建設 防犯カメラ商談__plaud-sample00.md"])

    def test_uncertain_person_not_created(self):
        self.assertIn(("人物", "山田太郎.md"), self.by)
        self.assertNotIn(("人物", "スズキ.md"), self.by)

    def test_minutes_content(self):
        md = next(f["content"] for f in self.files if f["folder"] == "議事録")
        self.assertIn("recorded_at: 2026-10-01T15:00+09:00", md)
        self.assertIn('source_id: "plaud:of_sample', md)
        self.assertIn("[[人物/山田太郎|山田太郎]]（山田建設） — 社長", md)
        self.assertIn("スズキ（聞き取り要確認）", md)
        self.assertIn("2026-10-01(木) 15:00 JST", md)
        self.assertIn("✅確定 2026-10-15 10:00", md)
        self.assertIn("❓要確認 日時未定 次回打合せ", md)
        self.assertIn("- [ ] 山田さんへ4台構成の見積を送付 [P2] 📅 2026-10-09", md)
        self.assertIn("山田さん：設置場所の図面を送付（相手の対応待ち）", md)
        self.assertNotIn("090-1234-5678", md)

    def test_stub_dedup_within_batch(self):
        files = rn.render_all([SAMPLE, SAMPLE], "2026-10-08T12:00+09:00")
        names = [(f["folder"], f["filename"]) for f in files]
        self.assertEqual(len([n for n in names if n[0] == "人物"]), 1)

    def test_self_person_not_created(self):
        d = copy.deepcopy(SAMPLE)
        d["people"].append({"name": "石原さん", "certain": True})
        files = rn.render_all([d], "2026-10-08T12:00+09:00")
        self.assertNotIn(("人物", "石原.md"), {(f["folder"], f["filename"]) for f in files})
        md = next(f["content"] for f in files if f["folder"] == "議事録")
        self.assertNotIn("[[人物/石原]]", md.split("---")[1])

    def test_invalid_raises(self):
        d = copy.deepcopy(SAMPLE)
        d["summary"] = ""
        with self.assertRaises(rn.ValidationError):
            rn.render_all([d])


class TestCli(unittest.TestCase):
    def test_render_cli(self):
        with tempfile.TemporaryDirectory() as td:
            sample = HERE.parent / "samples" / "sample_extraction.json"
            r = subprocess.run([sys.executable, str(HERE.parent / "scripts" / "render_notes.py"), "render",
                                str(sample), "--out", td, "--generated-at", "2026-10-08T12:00+09:00"],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            manifest = json.loads((Path(td) / "manifest.json").read_text(encoding="utf-8"))
            self.assertTrue(any(m["folder"] == "処理ログ" for m in manifest))
            for m in manifest:
                self.assertTrue(Path(m["local_path"]).exists())


if __name__ == "__main__":
    unittest.main()
