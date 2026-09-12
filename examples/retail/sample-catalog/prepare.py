"""Prepare the public two-product catalog example into a new external package."""

import argparse
import hashlib
import json
import shutil
from datetime import date, timedelta
from pathlib import Path


def prepare(destination: Path) -> None:
    source = Path(__file__).resolve().parent
    retail = source.parent
    destination.mkdir(parents=True, exist_ok=False)
    data = destination / "data"
    images = destination / "images"
    data.mkdir()
    images.mkdir()

    def write(name: str, value: object) -> None:
        (data / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")

    # This fixture has one structured excerpt; customer PDF/OCR work happens offline.
    catalog_text = (source / "source-catalog.md").read_text()
    products = json.loads(catalog_text.split("```json\n", 1)[1].split("```", 1)[0])
    manifest = {
        "version": 1,
        "dataset_id": "playroom-sample",
        "store_name": "ACME Playroom Sample",
        "simulated": True,
    }
    (destination / "dataset.json").write_text(json.dumps(manifest, indent=2) + "\n")
    write("catalog.json", {"store_name": manifest["store_name"], "products": products})
    translated_fields = {"title", "short_description", "long_description", "attributes", "specs"}
    write(
        "translations.json",
        {
            "en": {
                p["product_id"]: {k: v for k, v in p.items() if k in translated_fields}
                for p in products
            },
            "zh": json.loads((source / "translations-zh.json").read_text()),
        },
    )
    provenance = []
    for product in products:
        filename = product["image_url"].removeprefix("/products/")
        image = retail / "storefront-web/public/products" / filename
        shutil.copy2(image, images / filename)
        provenance.append(
            {
                "product_id": product["product_id"],
                "source": f"source-catalog.md#{product['product_id']}",
                "image": filename,
                "sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
                "association": "upstream category illustration, not a model-specific photograph",
                "missing": ["model-specific photograph"]
                + ([] if "specs" in product else ["specs", "long_description"]),
            }
        )
    shutil.copy2(retail / "storefront-web/public/products/IMAGE-CREDITS.md", images)
    shutil.copy2(source / "source-catalog.md", data)
    write("provenance.json", {"products": provenance, "operating_data": "simulated"})
    write(
        "users.json",
        {
            "users": [
                {
                    "user_id": "demo-user",
                    "display_name": "Priya",
                    "default_location": "Maple Heights",
                    "preferences": {"purpose": "family games for a small apartment"},
                }
            ]
        },
    )
    # Simulate one unit/order/product/day. Metrics are derived from the same orders.
    today = date.today()
    orders, daily = [], []
    for offset in range(30, 0, -1):
        day = today - timedelta(days=offset)
        day_orders = [
            {
                "order_id": f"SIM-{day:%Y%m%d}-{p['product_id']}",
                "user_id": "demo-user",
                "status": "delivered",
                "placed_at": f"{day}T10:00:00Z",
                "items": [
                    {
                        "product_id": p["product_id"],
                        "title": p["title"],
                        "quantity": 1,
                        "price": p["price"],
                    }
                ],
                "total": p["price"],
            }
            for p in products
        ]
        orders.extend(day_orders)
        daily.append(
            {
                "date": str(day),
                "sales": sum(o["total"] for o in day_orders),
                "orders": len(day_orders),
                "traffic": 100,
                "kids_room_sales": 0,
            }
        )
    write("orders.json", {"orders": orders})
    write("merchant_metrics.json", {"currency": "USD", "daily": daily})
    write(
        "merchant_inventory.json",
        {
            "inventory": [
                {
                    "product_id": p["product_id"],
                    "stock": stock,
                    "threshold": 8,
                    "sales_last_30d": 30,
                }
                for p, stock in zip(products, (3, 20), strict=True)
            ]
        },
    )
    write("merchant_campaigns.json", {"campaigns": []})
    write("merchant_messages.json", {"issues": []})
    write("memory-seed.json", {})
    # Keep the official demo's fulfillment contract; it is a simulated store policy.
    shutil.copy2(retail / "data/policies.json", data)
    write(
        "simulation.json",
        {
            "simulated": True,
            "prepared_on": str(today),
            "assumptions": [
                "All prices, reviews, orders, traffic, inventory and policies are fictional.",
                "One order per product per day for 30 days; one unit in each order.",
                "Opening stock 33/50 minus 30 sold yields 3/20 remaining units.",
                "Traffic is 100 visits/day; no campaign or buyer-message records were supplied.",
                "Re-run preparation before a later recording: upstream metrics shift by weeks while finished orders keep their dates.",
            ],
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="new directory outside the repository")
    prepare(parser.parse_args().destination.expanduser().resolve())
