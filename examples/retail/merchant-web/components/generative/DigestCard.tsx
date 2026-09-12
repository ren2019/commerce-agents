// Copyright 2026 Anthropic PBC
// SPDX-License-Identifier: Apache-2.0

import { CHANGE_STATUS, DigestList, DigestRow, formatMoney, formatNumber, GenCard, GenCardHeader, type IconName, plural, type Tone, useDemoLanguage } from "web-shared";
import { INVENTORY_KINDS } from "@/lib/kinds";
import type { DigestEntry, DigestPayload } from "@/lib/types";

const KINDS: Record<DigestEntry["kind"], { icon: IconName; tone: Tone }> = {
  ...INVENTORY_KINDS,
  order_issue: { icon: "inbox", tone: "danger" },
  metric: { icon: "chart", tone: "ok" },
  pending_change: { icon: "edit", tone: "violet" },
  note: { icon: "message", tone: "muted" },
};

/** Pending changes get no chip; approval stays on the change card. */
function triagePrompt(item: DigestEntry, language: string): { label: string; prompt: string } | null {
  const listingRef = item.listing ? `${item.listing.title} (${item.listing.listing_id})` : item.ref_id;
  switch (item.kind) {
    case "low_stock":
      return listingRef ? { label: "Draft restock", prompt: language === "zh" ? `为${listingRef}准备补货方案。` : `Draft a restock plan for ${listingRef}.` } : null;
    case "slow_mover":
      return listingRef ? { label: "Plan markdown", prompt: language === "zh" ? `为${listingRef}准备降价方案。` : `Plan a markdown for ${listingRef}.` } : null;
    case "order_issue":
      return {
        label: "Draft reply",
        prompt: language === "zh" ? `请协助处理订单${item.ref_id ?? ""}：${item.headline}` : item.ref_id ? `Help me handle order ${item.ref_id}: ${item.headline}` : `Help me handle this order issue: ${item.headline}`,
      };
    case "metric":
      return { label: "Ask why", prompt: language === "zh" ? `分析原因：${item.headline}` : `What's driving this: ${item.headline}?` };
    default:
      return null;
  }
}

function context(item: DigestEntry, language: string, t: (text: string) => string) {
  if (item.listing) {
    return (
      <span>
        {item.listing.listing_id} · {item.listing.stock === 0 ? t("sold out") : language === "zh" ? `库存${formatNumber(item.listing.stock)}件` : `${formatNumber(item.listing.stock)} in stock`} · {formatMoney(item.listing.price)}
      </span>
    );
  }
  if (item.change) {
    return (
      <span>
        {item.change.change_id} · {t(CHANGE_STATUS[item.change.status].label)}
      </span>
    );
  }
  return null;
}

export default function DigestCard({ payload, onPrefill }: { payload: DigestPayload; onPrefill?: (text: string) => void }) {
  const { language, t } = useDemoLanguage();
  const items = payload.items ?? [];
  return (
    <GenCard>
      <GenCardHeader title={payload.title ?? t("Needs attention")} aside={language === "zh" ? `${items.length}项` : plural(items.length, "item")} />
      <DigestList>
        {items.map((item, index) => {
          const triage = onPrefill ? triagePrompt(item, language) : null;
          const style = KINDS[item.kind] ?? KINDS.note;
          const soldOut = item.kind === "low_stock" && item.listing?.stock === 0;
          return (
            <DigestRow
              key={`${item.ref_id ?? item.headline}-${index}`}
              icon={style.icon}
              tone={soldOut ? "danger" : style.tone}
              headline={item.headline}
              why={item.why_it_matters}
              context={context(item, language, t)}
              action={triage ? { label: t(triage.label), onClick: () => onPrefill?.(triage.prompt) } : null}
            />
          );
        })}
      </DigestList>
    </GenCard>
  );
}
