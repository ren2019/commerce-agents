// Copyright 2026 Anthropic PBC
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useEffect, useState } from "react";
import { useDemoLanguage } from "./language";

type Loader<P> = () => Promise<P[] | null>;

const indexes = new WeakMap<object, Map<string, Promise<Record<string, unknown> | null>>>();

/** Cache successful reads per language; failed refreshes retain the last catalog. */
export function useCatalogIndex<P extends { product_id: string }>(
  load: Loader<P>,
): Record<string, P> {
  const { language } = useDemoLanguage();
  const [index, setIndex] = useState<Record<string, P>>({});
  useEffect(() => {
    let languages = indexes.get(load);
    if (!languages) {
      languages = new Map();
      indexes.set(load, languages);
    }
    let promise = languages.get(language) as Promise<Record<string, P> | null> | undefined;
    if (!promise) {
      promise = load().then((products) => {
        if (products === null) {
          languages.delete(language);
          return null;
        }
        return Object.fromEntries(products.map((product) => [product.product_id, product]));
      });
      languages.set(language, promise);
    }
    let mounted = true;
    void promise.then((value) => {
      if (mounted && value !== null) setIndex(value);
    });
    return () => {
      mounted = false;
    };
  }, [load, language]);
  return index;
}
