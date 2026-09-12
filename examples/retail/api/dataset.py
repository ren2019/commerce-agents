"""Validated external retail data packages; source files remain outside the repository."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from .mock_merchant import MockRetailMerchant
from .mock_retail import DATA_DIR, MockRetail


class Manifest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: int = 1
    dataset_id: str
    store_name: str
    logo: str | None = None
    simulated: bool = True


@dataclass
class Dataset:
    root: Path
    data_dir: Path
    images: Path
    manifest: Manifest
    warnings: list[str]


def local_asset(images: Path, reference: str) -> Path:
    path = (images / reference).resolve()
    if not path.is_relative_to(images.resolve()):
        raise ValueError(f"Image reference escapes images directory: {reference}")
    return path


def load_dataset(root: Path | None = None) -> Dataset:
    if root is None:
        return Dataset(
            DATA_DIR.parent,
            DATA_DIR,
            DATA_DIR.parent / "storefront-web/public/products",
            Manifest(dataset_id="retail", store_name="ACME"),
            [],
        )
    root = root.expanduser().resolve()
    try:
        manifest = Manifest.model_validate_json((root / "dataset.json").read_text())
        if manifest.version != 1:
            raise ValueError("dataset.json: supported version is 1")
        if not manifest.dataset_id.strip() or not manifest.store_name.strip():
            raise ValueError("dataset.json: dataset_id and store_name must not be empty")
        data_dir, images = root / "data", root / "images"
        if not images.is_dir():
            raise ValueError("images/: directory missing (may be empty)")
        catalog = json.loads((data_dir / "catalog.json").read_text())
        if catalog.get("store_name") != manifest.store_name:
            raise ValueError("catalog.json: store_name must match dataset.json")
        ids = []
        warnings = []
        for product in catalog["products"]:
            for record in [product, *product.get("variants", [])]:
                ids.append(record["product_id"])
                image = record.get("image_url")
                if image:
                    if not image.startswith("/products/"):
                        raise ValueError(
                            f"{record['product_id']}: image_url must start with /products/"
                        )
                    if not local_asset(images, image.removeprefix("/products/")).is_file():
                        warnings.append(f"{record['product_id']}: missing image {image}")
        if len(ids) != len(set(ids)):
            raise ValueError("catalog.json: duplicate product_id")
        storefront = MockRetail(data_dir)
        MockRetailMerchant(storefront, data_dir=data_dir)
        orders = json.loads((data_dir / "orders.json").read_text())
        users = json.loads((data_dir / "users.json").read_text())
        user_ids = {u["user_id"] for u in users["users"]}
        if len(user_ids) != len(users["users"]):
            raise ValueError("users.json: duplicate user_id")
        for row in json.loads((data_dir / "merchant_inventory.json").read_text())["inventory"]:
            if row["product_id"] not in ids:
                raise ValueError(f"merchant_inventory.json: unknown product {row['product_id']}")
        for row in json.loads((data_dir / "merchant_messages.json").read_text())["issues"]:
            if row.get("listing_id") and row["listing_id"] not in ids:
                raise ValueError(f"merchant_messages.json: unknown listing {row['listing_id']}")
        seed = data_dir / "memory-seed.json"
        if seed.exists():
            from commerce_common.types import MemoryFact

            for user_id, facts in json.loads(seed.read_text()).items():
                if user_id not in user_ids:
                    raise ValueError(f"memory-seed.json: unknown user {user_id}")
                for fact in facts:
                    MemoryFact.model_validate(fact)
        for order in orders["orders"]:
            if order["user_id"] not in user_ids:
                raise ValueError(f"{order['order_id']}: unknown user_id")
            for item in order["items"]:
                if item["product_id"] not in ids:
                    raise ValueError(f"{order['order_id']}: unknown product {item['product_id']}")
        translations = data_dir / "translations.json"
        if translations.exists():
            localized = json.loads(translations.read_text())
            if set(localized) - {"en", "zh"}:
                raise ValueError("translations.json: locales must be en or zh")
            for locale, products in localized.items():
                for product_id, fields in products.items():
                    if product_id not in ids:
                        raise ValueError(f"translations.json: unknown product {product_id}")
                    if set(fields) - {
                        "title",
                        "short_description",
                        "long_description",
                        "attributes",
                        "specs",
                        "aliases",
                    }:
                        raise ValueError(
                            f"translations.json: unsupported fields for {locale}/{product_id}"
                        )
                    for key, value in fields.items():
                        valid = (
                            isinstance(value, dict)
                            and all(
                                isinstance(k, str) and isinstance(v, str) for k, v in value.items()
                            )
                            if key in {"attributes", "specs"}
                            else isinstance(value, list) and all(isinstance(v, str) for v in value)
                            if key == "aliases"
                            else isinstance(value, str)
                        )
                        if not valid:
                            raise ValueError(
                                f"translations.json: invalid {locale}/{product_id}/{key}"
                            )
        if manifest.logo and not local_asset(images, manifest.logo).is_file():
            raise ValueError("dataset.json: logo file missing")
        return Dataset(root, data_dir, images, manifest, warnings)
    except (OSError, KeyError, ValueError) as error:
        raise ValueError(f"Invalid dataset {root}: {error}") from error


def state_directory() -> Path:
    import os

    return Path(
        os.environ.get("RETAIL_STATE_DIR", "~/.local/share/commerce-agent/retail")
    ).expanduser()


def selected_dataset() -> Dataset:
    import os

    explicit = os.environ.get("RETAIL_DATASET")
    if explicit:
        return load_dataset(Path(explicit))
    selection = state_directory() / "selected.json"
    if selection.exists():
        return load_dataset(Path(json.loads(selection.read_text())["runtime"]))
    return load_dataset()


def import_dataset(source: Path, state_dir: Path | None = None) -> Dataset:
    """Validate before atomically selecting a private runtime copy, leaving a live API intact."""
    import shutil
    import tempfile

    candidate = load_dataset(source)
    state_dir = state_dir or state_directory()
    state_dir.mkdir(parents=True, exist_ok=True)
    runtime = Path(tempfile.mkdtemp(prefix="dataset-", dir=state_dir))
    try:
        shutil.copy2(candidate.root / "dataset.json", runtime / "dataset.json")
        shutil.copytree(
            candidate.data_dir, runtime / "data", ignore=shutil.ignore_patterns(".memory-*.json")
        )
        shutil.copytree(candidate.images, runtime / "images")
        checked = load_dataset(runtime)
        baseline = runtime / "baseline"
        baseline.mkdir()
        shutil.copy2(runtime / "dataset.json", baseline / "dataset.json")
        shutil.copytree(runtime / "data", baseline / "data")
        shutil.copytree(runtime / "images", baseline / "images")
        selection = {
            "source": str(candidate.root),
            "runtime": str(runtime),
            "baseline": str(baseline),
        }
        with tempfile.NamedTemporaryFile(mode="w", dir=state_dir, delete=False) as handle:
            json.dump(selection, handle)
            pending = Path(handle.name)
        pending.replace(state_dir / "selected.json")
        return checked
    except Exception:
        shutil.rmtree(runtime)
        raise


def reset_dataset(state_dir: Path | None = None) -> Dataset:
    """Select a fresh runtime from the imported baseline, preserving the old runtime."""
    state_dir = state_dir or state_directory()
    selection_file = state_dir / "selected.json"
    if not selection_file.is_file():
        raise ValueError("Import a dataset before resetting it")
    selection = json.loads(selection_file.read_text())
    if "baseline" not in selection:
        raise ValueError("Re-import this dataset once to establish its reset baseline")
    return import_dataset(Path(selection["baseline"]), state_dir)
