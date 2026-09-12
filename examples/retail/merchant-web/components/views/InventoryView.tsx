// Copyright 2026 Anthropic PBC
// SPDX-License-Identifier: Apache-2.0

"use client";

import { AskButton, coverLabel, formatNumber, KindIcon, MiniBar, Notice, optionValuesLabel, PageHeader, Panel, Pill, plural, Skeleton, useResource, useDemoLanguage } from "web-shared";
import { fetchAlerts } from "@/lib/api";
import { INVENTORY_KINDS } from "@/lib/kinds";
import type { InventoryAlert } from "@/lib/types";

function AlertRow({ alert, onAskAssistant }: { alert: InventoryAlert; onAskAssistant: (text: string) => void }) {
  const { language, t } = useDemoLanguage();
  const style = INVENTORY_KINDS[alert.kind];
  const soldOut = alert.stock === 0;
  const low = alert.kind === "low_stock";
  const chosen = optionValuesLabel(alert, t);
  const name = chosen ? `${alert.title} in ${chosen}` : alert.title;
  const prompt = language === "zh" ? (low ? `为${alert.title}（${alert.listing_id}）准备补货方案。` : `为${alert.title}（${alert.listing_id}）准备降价方案。`) : low ? `Draft a restock plan for ${name} (${alert.listing_id}).` : `Plan a markdown for ${name} (${alert.listing_id}).`;
  return (
    <li className="flex items-center gap-3 px-[18px] py-3">
      <KindIcon icon={style.icon} tone={soldOut ? "danger" : style.tone} />
      <div className="min-w-0 flex-1">
        <div className="text-[13.5px] font-medium leading-snug text-(--ink)">
          {alert.title}
          {chosen ? <span className="font-normal text-(--ink-soft)"> · {chosen}</span> : null}
        </div>
        <div className="mt-0.5 flex flex-wrap items-center gap-x-1.5 gap-y-1 text-[12.5px] tabular-nums text-(--ink-soft)">
          <span>{alert.listing_id}</span>
          {alert.sales_last_30d != null ? <span>· {language === "zh" ? `近30天售出${formatNumber(alert.sales_last_30d)}件` : `${formatNumber(alert.sales_last_30d)} sold in 30 days`}</span> : null}
          {low && alert.threshold != null ? <span>· {language === "zh" ? `补货阈值${formatNumber(alert.threshold)}件` : `reorder at ${formatNumber(alert.threshold)}`}</span> : null}
          {low && alert.stock > 0 && alert.storefront_visible ? (
            <Pill tone="warn" dot>
              {language === "zh" ? `顾客端显示“仅剩${formatNumber(alert.stock)}件”` : `Storefront shows “Only ${formatNumber(alert.stock)} left”`}
            </Pill>
          ) : null}
          {soldOut && alert.storefront_visible === false ? <span>· {t("hidden from the storefront")}</span> : null}
        </div>
      </div>
      <div className="w-32 shrink-0 whitespace-nowrap text-right tabular-nums">
        <div className={`text-[15px] font-semibold ${soldOut ? "text-(--danger)" : low ? "text-(--warn)" : "text-(--ink)"}`}>
          {soldOut ? "0" : formatNumber(alert.stock)}
          <span className="ml-1 text-[11.5px] font-medium text-(--ink-soft)">{t("in stock")}</span>
        </div>
        <div className="mt-0.5 flex items-center justify-end gap-1.5 text-[11.5px] text-(--ink-soft)">
          {/* Stock against the reorder threshold: empty at zero, full at twice the threshold. */}
          {low && alert.threshold ? <MiniBar value={alert.stock / (alert.threshold * 2)} tone={soldOut ? "danger" : "warn"} /> : null}
          {alert.days_of_cover != null && !soldOut ? <span>{language === "zh" ? `约可销售${Math.round(alert.days_of_cover)}天` : coverLabel(alert.days_of_cover)}</span> : soldOut ? <span>{t("sold out")}</span> : null}
        </div>
      </div>
      <AskButton label={t(low ? "Draft restock" : "Plan markdown")} onClick={() => onAskAssistant(prompt)} />
    </li>
  );
}

export default function InventoryView({ refreshKey, onAskAssistant }: { refreshKey: number; onAskAssistant: (text: string) => void }) {
  const { language, t } = useDemoLanguage();
  const { data, failed } = useResource(fetchAlerts, [refreshKey, language]);

  const lowStock = (data?.inventory ?? [])
    .filter((alert) => alert.kind === "low_stock")
    .sort((a, b) => (a.days_of_cover ?? Infinity) - (b.days_of_cover ?? Infinity));
  const slowMovers = (data?.inventory ?? []).filter((alert) => alert.kind === "slow_mover");
  const tiedUp = slowMovers.reduce((sum, alert) => sum + alert.stock, 0);

  return (
    <div className="ac-reveal @container flex flex-col gap-4">
      <PageHeader
        title={t("Inventory")}
        subtitle={data ? language === "zh" ? `${lowStock.length}项库存不足或售罄 · ${slowMovers.length}项滞销，积压${formatNumber(tiedUp)}件` : `${lowStock.length} low or out of stock · ${plural(slowMovers.length, "slow mover")}${tiedUp ? ` with ${formatNumber(tiedUp)} units tied up` : ""}` : undefined}
      />
      {failed && !data ? (
        <Notice>{t("Inventory alerts could not be loaded.")}</Notice>
      ) : !data ? (
        <div className="grid gap-4 @4xl:grid-cols-2">
          <Skeleton className="h-72" />
          <Skeleton className="h-72" />
        </div>
      ) : (
        <div className="grid items-start gap-4 @4xl:grid-cols-2">
          <Panel title={t("Low stock")} subtitle={t("soonest to run out first")}>
            {lowStock.length === 0 ? (
              <p className="px-[18px] pb-4 text-[13.5px] text-(--ink-soft)">{t("No low-stock listings.")}</p>
            ) : (
              <ul className="divide-y divide-(--line)">
                {lowStock.map((alert) => (
                  <AlertRow key={alert.listing_id} alert={alert} onAskAssistant={onAskAssistant} />
                ))}
              </ul>
            )}
          </Panel>
          <Panel title={t("Slow movers")} subtitle={t("stock well above the last 30 days of sales")}>
            {slowMovers.length === 0 ? (
              <p className="px-[18px] pb-4 text-[13.5px] text-(--ink-soft)">{t("No slow movers.")}</p>
            ) : (
              <ul className="divide-y divide-(--line)">
                {slowMovers.map((alert) => (
                  <AlertRow key={alert.listing_id} alert={alert} onAskAssistant={onAskAssistant} />
                ))}
              </ul>
            )}
          </Panel>
        </div>
      )}
    </div>
  );
}
