// Copyright 2026 Anthropic PBC
// SPDX-License-Identifier: Apache-2.0

import { AgentApi } from "web-shared";
import type { CartPayload, Product, ProductDetails } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const api = new AgentApi(API_URL, "/api");

export const UNREACHABLE = "Couldn't reach the demo service. Check that it is running and try again.";

export async function fetchProducts(): Promise<Product[] | null> {
  const data = await api.get<{ products: Product[] }>("/products", { limit: "100" });
  return data?.products ?? null;
}

export function fetchProduct(productId: string): Promise<ProductDetails | null> {
  return api.get<ProductDetails>(`/products/${encodeURIComponent(productId)}`);
}

export async function addToCart(productId: string, quantity = 1): Promise<CartPayload | null> {
  const data = await api.post<{ cart: CartPayload }>("/cart/add", { product_id: productId, quantity });
  return data?.cart ?? null;
}

export type DatasetInfo = { dataset_id: string; store_name: string; logo: string | null; simulated: boolean; warnings: string[] };
export async function fetchDataset(): Promise<DatasetInfo | null> {
  const response = await fetch(`${API_URL}/api/dataset`);
  return response.ok ? response.json() : null;
}
