# 双语 AI for Commerce 演示手册

这是由演示者操作的本地案例，供现场展示或自行录屏。沿用官方 retail 顾客与商家故事；订单、支付与经营数据均为模拟，不开放客户自由体验。当前仍在完成最终验收，不能把本手册视为已通过人工操作复核。

## 从公开 fork 启动

需要 Python 3.11+、Node.js 22+ 和 npm。首次安装需要网络。展示分支为 `codex/bilingual-commerce-demo`。

```bash
git clone --branch codex/bilingual-commerce-demo https://github.com/ren2019/commerce-agents.git
cd commerce-agents
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
npm ci --prefix examples
```

在未跟踪的根目录 `.env` 配置自己的账户信息，不把真实密钥放进终端命令、录像或 Git：

```dotenv
RETAIL_MODEL_PROVIDER=deepseek
DEEPSEEK_API_KEY=填写自己的密钥
DEEPSEEK_MODEL=填写账户可用的模型标识
MERCHANT_REQUIRE_HOST_APPROVAL=1
```

本次实际验证的模型标识为 `deepseek-flash`。模型是否可用以自己的账户为准。两个角色、分析与记忆均使用该模型；不需要 Anthropic 密钥。使用的是 DeepSeek 的 Anthropic 兼容接口，不开启 thinking，也不使用 Anthropic 托管代码执行。若环境配置了 SOCKS 代理且提示缺少 `socksio`，在该虚拟环境补装 `socksio`。

```bash
.venv/bin/python scripts/run_demo.py retail --all --prod --no-reuse
```

以启动器打印的三个地址为准：默认 API 8000、顾客端 3000、商家端 3100；占用时会换端口。保留终端，使用 Ctrl-C 停止本次服务。更改模型配置、切换或重置数据后停止并重新运行该命令，再刷新两端页面。

语言按钮切换界面与后续回答。历史对话保留原语言；价格、币种、商品 ID 和购物车不随语言改变。录制另一语言的完整故事前重置数据并重新打开页面。

## 数据准备与图片

官方完整数据直接随代码运行。并非每个商品都有照片；已有图片为有出处的品类示意图，没有图片时显示占位，不把示意图当作精确型号证明。

客户资料保存在仓库之外。按[数据准备说明](retail-data-preparation.md)把产品目录册整理为带出处的商品记录、双语文案、图片和关联模拟业务数据。PDF 解析、图片裁切及人工确认属于准备阶段，演示运行时不直接读取原始目录 PDF。材质、尺寸、覆盖面积等未知参数留空，不能让 coding agent 猜测。

目录册交给 coding agent 时，同时提供：允许使用的产品范围、型号与原文页码、图片来源及使用范围、需保留的价格/币种、缺失资料、演示品牌及语言。逐项检查图片与型号对应关系。客户图片与数据不提交到公开 fork。

```bash
.venv/bin/python scripts/retail_dataset.py validate /absolute/customer-package
.venv/bin/python scripts/retail_dataset.py import /absolute/customer-package
```

准备好的数据集之间切换：

```bash
.venv/bin/python scripts/retail_dataset.py switch /absolute/another-package
```

每次复演恢复所选数据包的导入基线：

```bash
.venv/bin/python scripts/retail_dataset.py reset
```

上述成功操作后均需重启 API 并刷新两端。旧会话失效，购物车、暂存变更与运行期改动清空；源数据包不被修改。导入失败不会替换当前选择。不要同时设置 `RETAIL_DATASET`，它会绕过导入选择。默认运行目录为 `~/.local/share/commerce-agent/retail`，可用 `RETAIL_STATE_DIR` 指定独立演示目录。

可用公开的小数据包练习导入：

```bash
.venv/bin/python examples/retail/sample-catalog/prepare.py /tmp/playroom-demo
.venv/bin/python scripts/retail_dataset.py import /tmp/playroom-demo
```

它只有两个商品，用于检查品牌、图片、双语内容和导入；不用于完整露营或经营分析故事。完整版演示应使用完整 retail 数据。首次运行完整故事时可指定一个新的 `RETAIL_STATE_DIR`，避免加载之前导入的小数据包。

## 顾客故事

| 步骤 | 中文 | English |
| --- | --- | --- |
| 需求 | 下个月我和伴侣带6岁的孩子第一次露营，需要一顶帐篷，不要太难搬弄，最好低于250美元。 | I'm taking my partner and our 6-year-old camping for the first time next month. We need a tent — nothing too heavy to deal with, ideally under $250. |
| 比较 | 比较最合适的两款，主要看空间和搭建方便程度。 | Compare the top two options for me — mostly care about space and ease of setup. |
| 决策 | 家庭款听起来合适，加入购物车，也告诉我退货规则。 | The family one sounds right. Add it to my cart, and remind me what returns look like just in case. |

展开商品卡、比较卡与购物车，核对型号、数量、价格及资料依据。可继续点击模拟结账并查看订单状态；不会发生真实付款。切换语言后用另一语言搜索同一商品，核对 ID 和金额保持一致。

## 商家故事

| 步骤 | 中文 | English |
| --- | --- | --- |
| 晨间摘要 | 今天早上有哪些事项需要我关注？ | What needs my attention this morning? |
| 变更预览 | 为海洋墙贴按当前销售速度补足未来一个月的库存，并完善商品描述。先展示两个预览，不要直接执行。 | Restock the ocean wall decals with enough to cover the next month at the current pace, and fix that listing's description so it covers what's been missing. Show me both before anything goes live. |
| 聊天批准 | 看起来可以，批准补货。 | Looks right — approve the restock. |
| 产品线分析 | 儿童房装饰最近似乎很受欢迎。看数据，海洋主题这个月真的优于全店其他商品吗？ | Kids-room decor feels like it's having a moment. Pull the numbers — is the under-the-sea line really outperforming the rest of the store this month? |
| 两周归因 | 最近两周销售为什么变化，哪些品类或商品贡献了多少？ | Why did sales move over the last two weeks — which category or listings drove it, and by how much? |

第三步聊天必须不能执行变更。阅读卡片前后值和双语文案后，在卡片上点击“批准 / Approve”；两项变更分别批准。随后在商品页和顾客端回读，核对库存、描述、价格和缺失属性。不要批准编造材质或覆盖面积的描述；已有哑光表面信息不等于已知材料成分。

分析卡应保留实际时间窗口、数值与数据限制。公开数据只有儿童房具备独立按日销售字段，没有完整商品级日销售明细，因此不能把增长直接归因到某个型号，也不能证明主题、流量或价格造成了增长。模型摘要仍可能出现计数或因果表述错误，演示者应以原始数据、卡片及回读为依据；错误运行不能作为成功案例录像。

## 展示前检查与同步上游

```bash
.venv/bin/python scripts/verify_all.py
.venv/bin/python scripts/smoke_chat.py --url http://localhost:8000 --vertical retail
.venv/bin/python scripts/smoke_chat.py --url http://localhost:8000 --vertical retail --merchant
```

将 URL 换成实际 API 地址。验证脚本包含共享代码回归、部署 dry-run 和八个应用的生产构建；smoke 会调用真实模型并改变模拟业务状态，完成后再重置准备录制。

`origin` 应指向自己的公开 fork，`upstream` 指向官方源：

```bash
git remote -v
git remote add upstream https://github.com/anthropics/commerce-agents.git
git fetch upstream
```

已有 upstream 时无需重复 add。在工作区干净时从当前展示版本建立 `codex/upstream-review` 分支，合入待评审的 upstream 提交。先解决冲突、运行完整验证与双语真实故事，再决定纳入展示分支；不要让未回归的官方更新直接替换正在演示的版本。记录旧展示提交和新上游提交，必要时切回旧展示提交重新构建。

## 人工操作检查点

由演示者亲自完成：启动、中文与英文各一次顾客/商家操作、拒绝或批准预览、回读、数据切换与重置。检查字号、图片、长文案、按钮和录屏范围，确保密钥与私人数据不入镜。此项完成前，GitHub #8 保持未验收；不要求产出成品视频。
