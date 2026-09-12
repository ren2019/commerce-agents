// Copyright 2026 Anthropic PBC
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useDemoLanguage, AskLink, BagPanel, CheckoutButton, formatMoney, optionValuesLabel, plural, RemoveLink, Stepper, TotalRow, useCatalogIndex, useStoreFrame } from "web-shared";
import { fetchProducts } from "@/lib/api";
import { localizeOptionText } from "@/lib/format";
import { STORE_POLICY } from "@/lib/storePolicy";
import type { CartItem, CartPayload, Product } from "@/lib/types";
import { DeliveryPromise, ProductImage, ProductTitle } from "./ProductTile";

/** The policy says "over" the threshold, so a cart at exactly the threshold is not free. */
function FreeShippingMeter({ subtotal }: { subtotal: number }) {
  const { language, t } = useDemoLanguage();
  const threshold = STORE_POLICY.freeShippingThreshold;
  const free = subtotal > threshold;
  const remaining = threshold - subtotal;
  const pct = Math.min((subtotal / threshold) * 100, 100);
  return (
    <div data-free-shipping-meter className="mb-3">
      <div className={`text-[13px] ${free ? "font-semibold text-(--ok)" : "text-(--ink-2)"}`}>
        {free ? (
          <>{t("Free shipping on this order ✓")}</>
        ) : remaining > 0 ? (
          <>
            <span className="font-bold text-(--ink)">{formatMoney(remaining)}</span> {language === "zh" ? "即可包邮" : "away from free shipping"}
          </>
        ) : (
          <>{t("Anything more ships free")}</>
        )}
      </div>
      <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-(--well)">
        <div className={`h-full rounded-full transition-[width] duration-500 ease-out ${free ? "bg-(--ok)" : "bg-(--accent)"}`} style={{ width: `${pct}%` }} />
      </div>
      {!free ? <div className="mt-1 text-[11.5px] text-(--ink-soft)">{language === "zh" ? `订单金额超过${formatMoney(threshold)}，标准配送免运费。` : `Standard shipping is free on orders over ${formatMoney(threshold)}.`}</div> : null}
    </div>
  );
}

/** The listing behind a line; a variant's line borrows its family's brand and image. */
function asProduct(item: CartItem, catalog: Record<string, Product>): Product {
  const family = item.variant_of ? catalog[item.variant_of] : undefined;
  return (
    catalog[item.product_id] ?? {
      ...family,
      product_id: item.product_id,
      title: item.title,
      price: item.price,
      image_url: item.image_url ?? family?.image_url,
      options: undefined,
      option_values: item.option_values,
    }
  );
}

/** "the ACME Sleep Hybrid Mattress (queen)": what a message to the assistant calls a line. */
function lineName(item: CartItem, t: (text: string) => string): string {
  const chosen = localizeOptionText(optionValuesLabel(item), t);
  return chosen ? `${item.title} (${chosen})` : item.title;
}

/** The docked cart. Quantity and checkout are messages to the assistant, so every write is one it made. */
export default function CartPanel({ cart, checkoutStaged = false }: { cart: CartPayload | null; checkoutStaged?: boolean }) {
  const { ask } = useStoreFrame();
  const { language, t } = useDemoLanguage();
  const items = cart?.items ?? [];
  const count = cart?.item_count ?? 0;
  const catalog = useCatalogIndex(fetchProducts);

  return (
    <BagPanel
      title={t("Cart")}
      count={language === "zh" ? `${count}件商品` : plural(count, "item")}
      isEmpty={items.length === 0}
      empty={
        <>
          {t("Nothing in the cart yet.")}
          <br />
          {t("Ask ACME Assistant for anything in the store.")}
        </>
      }
      footer={
        <>
          {items.length ? <FreeShippingMeter subtotal={cart?.subtotal ?? 0} /> : null}
          <TotalRow label={language === "zh" ? `小计${count ? ` · ${count}件商品` : ""}` : count ? `Subtotal · ${plural(count, "item")}` : "Subtotal"} value={formatMoney(cart?.subtotal ?? 0, cart?.currency)} />
          <CheckoutButton staged={checkoutStaged} disabled={items.length === 0} prompt="Check out my cart." />
          {items.length ? (
            <div className="mt-2.5 flex justify-center">
              <AskLink label="Ask about this cart" prompt="Look over my cart: anything missing or worth swapping?" />
            </div>
          ) : null}
        </>
      }
    >
      <ul className="divide-y divide-(--line)">
        {items.map((item) => {
          const product = asProduct(item, catalog);
          return (
            <li key={item.product_id} className="ac-reveal flex gap-3 py-3 first:pt-0">
              <ProductImage product={product} className="h-16 w-16 shrink-0 rounded-[10px] !text-3xl" />
              <div className="min-w-0 flex-1">
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    {product.brand ? <div className="text-[10.5px] font-semibold uppercase tracking-[0.06em] text-(--ink-soft)">{product.brand}</div> : null}
                    {/* A two-line clamp cuts long names in half. */}
                    <ProductTitle title={item.title} className="line-clamp-3 text-[13.5px] font-semibold leading-snug text-(--ink)" />
                    {optionValuesLabel(item) ? <div className="text-[11.5px] text-(--ink-soft)">{localizeOptionText(optionValuesLabel(item), t)}</div> : null}
                  </div>
                  <div className="shrink-0 text-right">
                    <div className="text-[14px] font-bold tabular-nums text-(--ink)">{formatMoney(item.line_total, cart?.currency)}</div>
                    {item.quantity > 1 ? <div className="text-[11px] text-(--ink-soft)">{formatMoney(item.price, cart?.currency)} {language === "zh" ? "/件" : "each"}</div> : null}
                  </div>
                </div>
                <DeliveryPromise product={product} className="mt-0.5" />
                <div className="mt-2 flex items-center gap-2.5">
                  <Stepper
                    quantity={item.quantity}
                    itemTitle={lineName(item, t)}
                    onChange={(quantity) =>
                      ask(language === "zh" ? (quantity < 1 ? `从购物车移除${lineName(item, t)}。` : `将${lineName(item, t)}的数量改为${quantity}。`) : quantity < 1 ? `Remove the ${lineName(item, t)} from my cart.` : `Change the ${lineName(item, t)} quantity to ${quantity}.`)
                    }
                  />
                  <RemoveLink itemTitle={lineName(item, t)} onClick={() => ask(language === "zh" ? `从购物车移除${lineName(item, t)}。` : `Remove the ${lineName(item, t)} from my cart.`)} />
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </BagPanel>
  );
}
