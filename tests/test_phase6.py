from engine.progression import ProgressionSystem
from engine.save_manager import SaveManager


def test_progression_next_sector():
    p = ProgressionSystem()
    p.next_sector()
    assert p.sector == 2
    assert p.cores_required == 4


def test_save_manager_roundtrip(tmp_path):
    save = SaveManager(tmp_path / 'save.json')
    save.save({'sector': 7})
    assert save.load()['sector'] == 7
