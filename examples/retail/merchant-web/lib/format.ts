// Copyright 2026 Anthropic PBC
// SPDX-License-Identifier: Apache-2.0

/** Retail-specific labels on top of web-shared's formatters. */

import { formatDayMonth, formatMoney, plural, type RecordRowData, titleCase } from "web-shared";
import { ORDER_STATUS } from "./kinds";
import type { RecentOrder } from "./types";

const CATEGORY_LABELS: Record<string, string> = {
  "beauty-personal-care": "Beauty & personal care",
  fitness: "Fitness",
  "furniture-bedroom": "Furniture & bedroom",
  grocery: "Grocery",
  "home-kitchen": "Home & kitchen",
  "kids-room": "Kids' room",
  "office-electronics": "Office & electronics",
  "outdoor-camping": "Outdoor & camping",
  "pet-supplies": "Pet supplies",
  "toys-games": "Toys & games",
  travel: "Travel",
};

export function formatCategoryLabel(slug: string): string {
  return CATEGORY_LABELS[slug] ?? titleCase(slug.replaceAll("-", "_"));
}

export function orderRows(orders: RecentOrder[], language = "en", t: (text: string) => string = (text) => text): RecordRowData[] {
  return orders.map((order) => ({
    id: order.order_id,
    detail: language === "zh" ? `${order.items}件商品` : plural(order.items, "item"),
    sub: `${formatDayMonth(order.placed_at, language === "zh" ? "zh-CN" : "en-US")} · ${formatMoney(order.total)}`,
    status: { ...(ORDER_STATUS[order.status] ?? { tone: "muted" }), label: t(ORDER_STATUS[order.status]?.label ?? order.status.replaceAll("_", " ")) },
  }));
}
