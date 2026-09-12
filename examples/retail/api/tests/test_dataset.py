import json
import shutil

import pytest

from retail.api.dataset import load_dataset
from retail.api.mock_retail import DATA_DIR


@pytest.fixture
def package(tmp_path):
    shutil.copytree(DATA_DIR, tmp_path / "data", ignore=shutil.ignore_patterns(".memory-*.json"))
    shutil.copytree(DATA_DIR.parent / "storefront-web/public/products", tmp_path / "images")
    (tmp_path / "dataset.json").write_text(
        json.dumps({"dataset_id": "sample", "store_name": "ACME"})
    )
    return tmp_path


def test_upstream_data_can_be_loaded_as_external_package(package):
    dataset = load_dataset(package)
    assert dataset.manifest.dataset_id == "sample"
    assert dataset.data_dir == package / "data"
    assert dataset.warnings == []


def test_rejects_duplicate_product_identity(package):
    path = package / "data/catalog.json"
    data = json.loads(path.read_text())
    data["products"].append(data["products"][0])
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="duplicate product_id"):
        load_dataset(package)


def test_reports_missing_image_and_rejects_path_escape(package):
    path = package / "data/catalog.json"
    data = json.loads(path.read_text())
    data["products"][0]["image_url"] = "/products/not-present.webp"
    path.write_text(json.dumps(data))
    assert "AR-1001" in load_dataset(package).warnings[0]
    data["products"][0]["image_url"] = "/products/../../outside.webp"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="escapes images"):
        load_dataset(package)


def test_rejects_order_referencing_unknown_product(package):
    path = package / "data/orders.json"
    data = json.loads(path.read_text())
    data["orders"][0]["items"][0]["product_id"] = "unknown"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="unknown product"):
        load_dataset(package)


def test_import_failure_keeps_selected_runtime_and_source_unchanged(package, tmp_path):
    from retail.api.dataset import import_dataset

    state = tmp_path / "private-state"
    before = (package / "data/catalog.json").read_bytes()
    active = import_dataset(package, state)
    selection = (state / "selected.json").read_bytes()
    assert active.root != package
    (active.data_dir / ".memory-store.json").write_text("{}")
    assert not (package / "data/.memory-store.json").exists()
    assert (package / "data/catalog.json").read_bytes() == before
    manifest = package / "dataset.json"
    manifest.write_text('{"version":2,"dataset_id":"broken","store_name":"ACME"}')
    with pytest.raises(ValueError, match="supported version"):
        import_dataset(package, state)
    assert (state / "selected.json").read_bytes() == selection
    assert (active.data_dir / "catalog.json").read_bytes() == before


def test_reset_uses_imported_baseline_not_changed_source(package, tmp_path):
    from retail.api.dataset import import_dataset, reset_dataset

    state = tmp_path / "state"
    first = import_dataset(package, state)
    original = (first.data_dir / "catalog.json").read_bytes()
    (first.data_dir / ".memory-store.json").write_text('{"changed":true}')
    (package / "data/catalog.json").write_text("invalid changed source")
    restored = reset_dataset(state)
    assert restored.root != first.root
    assert (restored.data_dir / "catalog.json").read_bytes() == original
    assert not (restored.data_dir / ".memory-store.json").exists()
    assert (first.data_dir / ".memory-store.json").exists()
