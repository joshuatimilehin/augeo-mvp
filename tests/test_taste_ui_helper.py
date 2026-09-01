from creative.reasoning.taste_ui_helper import save_taste_label
import os


def test_save_taste_label_tmp_path(tmp_path):
    record = {"chosen": "0", "note": "nice"}
    out = tmp_path / "out.jsonl"
    path = save_taste_label(record, out_path=str(out))
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().strip().splitlines()
    assert len(lines) == 1
    assert "nice" in lines[0]
