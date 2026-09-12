// Copyright 2026 Anthropic PBC
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useCallback, useEffect, useState } from "react";
import { DemoLanguageProvider, LanguageSwitch, useDemoLanguage, type AgentEvent, formatMoney, OrdersView, plural, StoreShell, type StoreView, upcoming, useAgentTurn, useResource, useSession } from "web-shared";
import CartPanel from "@/components/CartPanel";
import Chat from "@/components/Chat";
import HomeView from "@/components/views/HomeView";
import { api, fetchDataset, UNREACHABLE } from "@/lib/api";
import { NOUNS, OrderThumb } from "@/lib/orders";
import { chinese } from "@/lib/chinese";
import type { CartPayload } from "@/lib/types";

type View = "assistant" | "orders";



function Wordmark({ name, logo, simulated }: { name: string; logo: string | null; simulated: boolean }) {
  return (
    <span className="flex items-center gap-2.5 pr-1">
      <span aria-hidden className="grid h-[30px] w-[30px] place-items-center rounded-lg bg-(--ink) text-[15px] font-bold text-(--surface)">
        {logo ? <img src={api.assetUrl(logo) ?? undefined} alt="" className="h-full w-full object-contain" /> : name.slice(0, 1)}
      </span>
      <span><span className="block text-[17px] font-bold tracking-[-0.02em] text-(--ink)">{name}</span>{simulated && <span className="block text-[10px] text-(--ink-muted)">Simulated data / 模拟数据</span>}</span>
    </span>
  );
}

function ordersSubtitle(upcomingCount: number, late: number, language: string): string {
  if (language === "zh") return late ? `${late}笔订单延误。可以询问原因，也可以咨询已收货商品的退货。` : `${upcomingCount}笔订单配送中。可以询问订单，也可以咨询已收货商品的退货。`;
  return late ? `${plural(late, "order")} running late. Ask why, or ask about a return on anything delivered.` : `${plural(upcomingCount, "order")} on the way. Ask about any of them, or about a return on anything delivered.`;
}

export default function StorefrontPage() {
  return <DemoLanguageProvider api={api} chinese={chinese}><Storefront /></DemoLanguageProvider>;
}

function Storefront() {
  const { language, t } = useDemoLanguage();
  const session = useSession(api);
  const { data: dataset } = useResource(fetchDataset, []);
  const store = dataset ?? { store_name: "ACME", logo: null, simulated: false };
  const storeName = store.store_name;
  const [view, setView] = useState<View>("assistant");
  const [cart, setCart] = useState<CartPayload | null>(null);
  // A staged checkout owns the panel's primary action until the cart changes again.
  const [checkoutStaged, setCheckoutStaged] = useState(false);
  const [panelOpen, setPanelOpen] = useState(false);

  const handleCartUpdate = useCallback((next: CartPayload) => {
    setCart(next);
    setCheckoutStaged(false);
  }, []);

  const onEvent = useCallback(
    (event: AgentEvent) => {
      if (event.type === "cart_update") handleCartUpdate(event.data.cart as CartPayload);
      else if (event.type === "ui" && event.data.component === "checkout") setCheckoutStaged(true);
    },
    [handleCartUpdate],
  );

  const chat = useAgentTurn(api, { ...session, unreachable: UNREACHABLE, onEvent });
  // A reply may have started a return, so orders re-read after each one.
  const { data: orders, failed: ordersFailed } = useResource(session.sessionId ? () => api.fetchOrders() : null, [session.sessionId, chat.completed, language]);

  useEffect(() => {
    if (session.sessionId) void api.fetchCart<CartPayload>().then((next) => next && setCart(next));
  }, [session.sessionId, language]);

  const late = (orders ?? []).filter((order) => order.status === "delayed").length;
  const views: StoreView<View>[] = [
    { id: "assistant", label: t("Assistant"), icon: "spark" },
    { id: "orders", label: t("Orders"), icon: "box", attention: late ? { count: late, label: `${late} ${t("delayed")}` } : null },
  ];
  const shopper = session.shopper ?? { name: t("Guest") };
  const cartSummary = cart ?? { item_count: 0, subtotal: 0, currency: "USD" };
  const count = cartSummary.item_count;

  return (
    <StoreShell
      brand={<Wordmark name={storeName} logo={store.logo} simulated={store.simulated} />}
      actions={<LanguageSwitch disabled={chat.busy} />}
      views={views}
      view={view}
      onViewChange={setView}
      chat={chat}
      api={api}
      assistantName={`${storeName} ${t("Assistant")}`}
      shopper={shopper}
      bag={{ label: t("Cart"), count, noun: "item", figure: count ? formatMoney(cartSummary.subtotal, cartSummary.currency) : null }}
      panel={<CartPanel cart={cart} checkoutStaged={checkoutStaged} />}
      panelOpen={panelOpen}
      onPanelOpenChange={setPanelOpen}
      placeholder={t(view === "orders" ? "Ask about an order, a return, a delivery…" : "Ask about a product, a project, an order…")}
    >
      {/* The conversation stays mounted under the other view so its cards keep their state. */}
      <div className={view === "assistant" ? "h-full" : "hidden"}>
        <Chat chat={chat} onCartUpdate={handleCartUpdate} home={<HomeView shopperName={shopper.name} orders={orders} ordersFailed={ordersFailed} onSeeOrders={() => setView("orders")} />} />
      </div>
      {view === "orders" ? (
        <OrdersView
          orders={orders}
          failed={ordersFailed}
          nouns={NOUNS}
          subtitle={orders ? ordersSubtitle(upcoming(orders).length, late, language) : undefined}
          thumb={(order) => <OrderThumb order={order} />}
        />
      ) : null}
    </StoreShell>
  );
}
