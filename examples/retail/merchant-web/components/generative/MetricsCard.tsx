// Copyright 2026 Anthropic PBC
// SPDX-License-Identifier: Apache-2.0

import { ChangeChip, formatMoney, formatNumber, formatPeriodLabel, formatRate, GenCard, GenCardHeader, Sparkline, titleCase, useDemoLanguage } from "web-shared";
import type { MetricEntry, MetricsPayload } from "@/lib/types";

const CURRENCY_METRICS = new Set(["sales", "average_order_value", "revenue", "spend"]);
const RATE_METRICS = new Set(["conversion_rate", "return_rate", "click_through_rate"]);

function metricLabel(metric: string): string {
  if (metric === "average_order_value") return "Average order";
  return titleCase(metric);
}

function metricValue(entry: MetricEntry): string | null {
  if (entry.value == null) return null;
  if (CURRENCY_METRICS.has(entry.metric)) return formatMoney(entry.value, entry.currency ?? "USD", { whole: entry.value >= 1000 });
  if (RATE_METRICS.has(entry.metric)) return formatRate(entry.value);
  return formatNumber(entry.value);
}

export default function MetricsCard({ payload }: { payload: MetricsPayload }) {
  const { language, t } = useDemoLanguage();
  const metrics = payload.metrics ?? [];
  // Analysis keeps the SQL category key; only its visible label is translated.
  const label = (text: string) => language === "zh" ? t(text).replace(/\bkids-room\b/gi, "儿童房") : text;
  return (
    <GenCard>
      <GenCardHeader title={label(payload.title ?? "Performance")} aside={payload.period ? t(formatPeriodLabel(payload.period, language === "zh" ? "zh-CN" : "en-US")) : null} />
      <div className="mt-2 grid grid-cols-2 border-t border-(--line) [&>*:nth-child(even)]:border-l [&>*:nth-child(n+3)]:border-t [&>*]:border-(--line)">
        {metrics.map((entry, index) => {
          const value = metricValue(entry);
          const points = entry.series?.points?.map((point) => point.value);
          return (
            <div key={`${entry.metric}-${index}`} className="px-3.5 py-3">
              <div className="text-[12px] font-medium text-(--ink-soft)">{label(metricLabel(entry.metric))}</div>
              <div className="mt-1 flex items-baseline gap-2">
                {value != null ? <span className="text-[20px] font-semibold leading-none tracking-[-0.02em] tabular-nums text-(--ink)">{value}</span> : null}
                <ChangeChip changePct={entry.change_pct} />
              </div>
              {points && points.length > 1 ? <Sparkline points={points} height={34} label={language === "zh" ? `${label(metricLabel(entry.metric))}趋势` : `${metricLabel(entry.metric)} trend`} className="mt-2" /> : null}
              {entry.note ? <div className="mt-1.5 text-[11.5px] leading-snug text-(--ink-soft)">{language === "zh" ? label(entry.note).replace(/^computed(?= — |$)/, "已计算") : entry.note}</div> : null}
            </div>
          );
        })}
      </div>
    </GenCard>
  );
}
