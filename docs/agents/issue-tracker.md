# Issue tracker: GitHub

Issues 和规格归属 ren2019/commerce-agents，使用 gh CLI 操作。
所有操作显式指定 --repo ren2019/commerce-agents，
不依赖当前目录的默认 remote。

- 发布规格：创建 GitHub issue。
- 读取任务：读取 issue 正文、标签和评论。
- 发布前检查已有 issue，避免重复创建。
- 多行正文写入临时文件，通过 --body-file 传入。
- 标签映射见 triage-labels.md。
- 仓库不存在或 Issues 未开启时，先完成仓库配置，
  不回退到 anthropics/commerce-agents。

PRs as a request surface: no.
