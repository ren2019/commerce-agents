"""Exercise complete application rebuilds around dataset selection and reset."""

import asyncio
import importlib
import json
import shutil

from fastapi.testclient import TestClient

from merchant_agent import InventoryActionItem, MerchantSessionContext
from retail.api import main
from retail.api import merchant as merchant_module
from retail.api.dataset import import_dataset, reset_dataset
from retail.api.tests.test_dataset import package  # noqa: F401


def test_switch_and_reset_clear_both_roles(package, tmp_path, monkeypatch):  # noqa: F811
    state = tmp_path / "state"
    monkeypatch.setenv("RETAIL_STATE_DIR", str(state))
    monkeypatch.delenv("RETAIL_DATASET", raising=False)
    merchant_backends = []
    original = merchant_module.MockRetailMerchant

    def capture(*args, **kwargs):
        backend = original(*args, **kwargs)
        merchant_backends.append(backend)
        return backend

    monkeypatch.setattr(merchant_module, "MockRetailMerchant", capture)
    second = tmp_path / "package-b"
    second.mkdir()
    shutil.copytree(package / "data", second / "data")
    shutil.copytree(package / "images", second / "images")
    (second / "dataset.json").write_text(json.dumps({"dataset_id": "b", "store_name": "ACME B"}))
    catalog = json.loads((second / "data/catalog.json").read_text())
    catalog["store_name"] = "ACME B"
    (second / "data/catalog.json").write_text(json.dumps(catalog))
    import_dataset(package, state)
    old_shopper = old_operator = None
    try:
        for action, expected, mutate in [
            (None, "sample", True),
            (lambda: import_dataset(second, state), "b", False),
            (lambda: import_dataset(package, state), "sample", True),
            (lambda: reset_dataset(state), "sample", False),
        ]:
            if action:
                action()
            importlib.reload(main)
            with TestClient(main.app, base_url="http://localhost") as client:
                assert client.get("/api/dataset").json()["dataset_id"] == expected
                if old_shopper:
                    assert client.get("/api/cart", headers=old_shopper).status_code == 401
                    assert (
                        client.get("/api/merchant/overview", headers=old_operator).status_code
                        == 401
                    )
                shopper = {
                    "X-Session-Id": client.post(
                        "/api/session", json={"user_id": "demo-user"}
                    ).json()["session_id"]
                }
                operator = {
                    "X-Session-Id": client.post("/api/merchant/session").json()["session_id"]
                }
                assert client.get("/api/cart", headers=shopper).json()["item_count"] == 0
                facts = client.get("/api/memory", headers=shopper).json()["facts"]
                assert len(facts) == 3
                overview = client.get("/api/merchant/overview", headers=operator).json()
                assert overview["recent_changes"] == []
                listing = client.get("/api/merchant/listings/AR-2102", headers=operator).json()
                assert listing["listing"]["stock"] == 3
                if mutate:
                    # Same provenance fixture used by the existing API contract tests.
                    record = main.host.sessions.require(shopper["X-Session-Id"])
                    record.state.remember_products([main.backend.product("AR-1301")])
                    main.host.sessions.save(record)
                    added = client.post(
                        "/api/cart/add",
                        headers=shopper,
                        json={"product_id": "AR-1301", "quantity": 1},
                    )
                    assert added.status_code == 200, added.text
                    assert client.get("/api/cart", headers=shopper).json()["item_count"] == 1
                    assert (
                        client.request(
                            "DELETE", "/api/memory", headers=shopper, json={"key": facts[0]["key"]}
                        ).status_code
                        == 200
                    )
                    backend = merchant_backends[-1]
                    context = MerchantSessionContext(
                        session_id=operator["X-Session-Id"],
                        merchant_id="acme-retail",
                        operator="Avery",
                    )
                    change = asyncio.run(
                        backend.stage_inventory_action(
                            context,
                            [
                                InventoryActionItem(
                                    listing_id="AR-2102", action="restock", quantity=24
                                )
                            ],
                        )
                    )
                    # Seed an applied state through the existing backend test seam;
                    # this test verifies reset, not model/approval provenance.
                    asyncio.run(backend.apply_change(context, change.change_id))
                    assert (
                        client.get("/api/merchant/listings/AR-2102", headers=operator).json()[
                            "listing"
                        ]["stock"]
                        == 27
                    )
                    asyncio.run(
                        backend.stage_inventory_action(
                            context,
                            [
                                InventoryActionItem(
                                    listing_id="AR-2102", action="restock", quantity=1
                                )
                            ],
                        )
                    )
                old_shopper, old_operator = shopper, operator
    finally:
        monkeypatch.delenv("RETAIL_STATE_DIR")
        importlib.reload(main)
