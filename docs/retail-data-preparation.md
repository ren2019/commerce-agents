# 从目录资料准备演示数据集

把本文件、原始目录所在路径和仓库外的输出路径交给 coding agent。成品是可由 `scripts/retail_dataset.py` 导入的目录；原始 PDF、OCR、图片裁剪都在准备阶段完成。首版只处理演示者整理后导入的数据，不提供网页上传册子或以图搜商品。

## 给 coding agent 的任务

1. 清点用户提供的目录、价格表、图片和品牌素材。在输出目录记录文件名、版本、SHA-256、适用范围及允许展示范围。客户资料保存在仓库之外；只用用户提供的资料制作工业案例。
2. 逐页提取选定商品。每个型号建立稳定 `product_id`，记录原始型号、页码、表格行及参数原文。区分系列与可购买变体，逐个核对尺寸、单位、额定值、选配范围和型号后缀。OCR 无法确定的内容写进缺失清单；商品参数不推测。型号或关键选型参数不明确的商品先排除，并说明原因。
3. 为每个商品建立图片映射：原文件/页码、裁剪区域、目标文件、关联型号、图片类型、校验摘要。打开每张导出的图片与目录对照，检查多型号共图、尺寸图、低清图及文字截断。只有来源证明对应型号时才记为型号图；系列图、品类示意图明确标注。缺图留空或记录缺失，不挪用其他型号图片。将允许使用的图转为本地 WebP/PNG/JPEG，保留原图；产品引用 `/products/文件名`。
4. 写规范记录（`catalog.json.source_language` 为 `en` 或 `zh`，默认 `en`）及 `translations.json` 的中英文内容；两种语言保留相同型号、数值、单位、币种和参数边界。中文检索别名另列，不改商品 ID。原文缺失的技术说明保持缺失；翻译不增加性能或认证。当前双语显示和跨语言搜索由 #4/#5 交付，侧车文件通过校验不代表这些功能已验收。
5. 用客户提供的经营资料，或生成明确标记为模拟的经营资料。订单行指向存在的商品/变体与用户；金额等于行项目合计；库存与 `in_stock` 一致。销量、指标由同一订单表汇总，解释时间范围、流量、成本和初始库存假设。政策沿用 demo 时标为模拟政策，不能代表客户条款。没有来源的买家信息与活动可用空列表。将数据来源、缺失项和模拟假设分别写入 `data/provenance.json` 与 `data/simulation.json`。
6. 执行下述校验和双端回读。修复错误后再导入；交付商品数、图片覆盖率、缺失清单、模拟字段清单及实际回读证据。仅验证数据准备时使用目录浏览、详情、订单和库存接口；真实模型故事另按对应 issue 验收。

## 包结构与校验边界

`examples/retail/api/dataset.py` 是加载规则的权威实现，`examples/retail/data/` 是完整字段样例。最小公开准备例见 [sample-catalog](../examples/retail/sample-catalog/README.md)。

| 文件 | 内容与关联 |
|---|---|
| `dataset.json` | `version: 1`、稳定 `dataset_id`、`store_name`；可选 `logo` 为 images 内相对路径。经营数据有模拟内容时设 `simulated: true`，双端显示模拟标识。 |
| `data/catalog.json` | 同名 `store_name`、`products`；稳定 ID、名称、品牌、分类、价格及币种、库存状态、图片。`attributes`/`specs` 保存来源参数；可购买变体必须有独立 ID。必需字段以 ProductDetails 模型为准。 |
| `data/policy-translations.json` | 可选；`en`、`zh` → policy_id → `title`、`content`、`aliases`。只允许现有政策 ID，aliases 为字符串列表；保留时限、费用和例外条件。 |
| `data/translations.json` | `en`、`zh` → product_id → `title`、`short_description`、`long_description`、`attributes`、`specs`、`aliases`、`review_highlights`；参数值为字符串，aliases 和 review_highlights 为字符串列表。没有原文的字段可省略。 |
| `data/users.json` | `users`；保留 `demo-user` 供默认演示身份使用，其他用户与订单关联。仅用虚构身份或允许展示的匿名身份。 |
| `data/orders.json` | `orders`；每行 ID、用户、状态、时间、商品行及金额。币种保持统一。 |
| `data/policies.json` | `policies`；配送与退换条款应与 mock backend 的履约规则一致。目录本身通常没有这些条款。 |
| `data/merchant_inventory.json` | `inventory`；商品 ID、库存、阈值、销量，按需成本/退货率。变体库存与可售状态一致。 |
| `data/merchant_metrics.json` | `currency`、非空 `daily`；日期、销售额、订单数、流量，按需分群指标。使用完整订单生成汇总，标注统计范围。 |
| `data/merchant_campaigns.json`、`data/merchant_messages.json` | 分别为 `campaigns`、`issues`，可为空。存在时检查活动及问题对应的订单/商品，不能保留旧案例引用。 |
| `data/memory-seed.json` | 可选用户 ID → 初始事实列表；只提供本数据集相关记忆。 |
| `images/` | 图片及可选 Logo；保留来源/许可说明，禁止引用仓库外路径。 |

校验器检查加载模型、重复 ID、主要外键、图片路径和翻译类型；图片与型号的语义对应、参数真实性、订单金额及指标口径需要准备阶段核对。缺图会给 warning，商品显示默认占位；错误包不会替换当前选择。

官方 demo 会在运行时移动日期：指标按整周移动，运输中订单按天移动，已完成订单默认保留日期。录制前按当前日期重新准备经营数据，并核对展示窗口；不要把这个演示时间机制当成真实经营报表。

## 导入和回读

从仓库根目录，用实际的外部目录替换 `/absolute/package`：

```bash
.venv/bin/python scripts/retail_dataset.py validate /absolute/package
.venv/bin/python scripts/retail_dataset.py import /absolute/package
```

停止并重新启动 retail API，刷新顾客端和商家端。CLI 会选择一份独立运行副本；详见 [切换与重置](../examples/retail/README.md#switch-and-reset)。使用相同的 `RETAIL_STATE_DIR`，清除会覆盖 CLI 选择的 `RETAIL_DATASET` 环境变量。

核对 `/api/dataset` 的品牌、模拟标识和 warnings；创建两端会话，再从购物商品详情和商家 listing 详情读取相同 ID、图片、价格和库存。浏览器打开两端，检查图片、模拟标识、订单和低库存提示。导入校验通过与模型闭环运行通过分别报告。
