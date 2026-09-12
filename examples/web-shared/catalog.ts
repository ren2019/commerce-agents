// Copyright 2026 Anthropic PBC
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useEffect, useState } from "react";
import { useDemoLanguage } from "./language";

type Loader<P> = () => Promise<P[] | null>;

const indexes = new WeakMap<object, Map<string, Promise<Record<string, unknown>>>>();

/** Loaded once per page, keyed on `load`; empty until then and when the API is down. */
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
    let promise = languages.get(language) as Promise<Record<string, P>> | undefined;
    if (!promise) {
      promise = load().then((products) =>
        Object.fromEntries((products ?? []).map((product) => [product.product_id, product])),
      );
      languages.set(language, promise);
    }
    let mounted = true;
    void promise.then((value) => {
      if (mounted) setIndex(value);
    });
    return () => {
      mounted = false;
    };
  }, [load, language]);
  return index;
}
