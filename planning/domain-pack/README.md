# domain-pack/ — 领域包目录

每个领域一个子目录（`ai/` 为首发）。包 = **传感器 + 判断标准**（plan §4.4）：部署时内容落到 AIHOT 实例的 `industry/`，本目录是开发与评审载体（不动实例直到 Phase B 部署门槛通过）。

| 文件 | 说明 |
|---|---|
| `ai/manifest.json` | 版本/品牌占位/feature 开关/依赖 key/部署注记 |
| `ai/sources.json` | 三支柱信源初稿（json_list/rss/web_list/x_search），$comment 标注部署时试抓校验项 |
| `ai/taxonomy.draft.ts` | 分类体系初稿（models/environment/skills/compute/discussion）；key 上线后不可改，上线前定稿 |
| `ai/prompts-selection-pillars.md` | 三支柱判断标准 + 一票否决负类（并入 prefilter/selection-score） |
| `ai/gold-selection-seed.jsonl` | A0 首批 gold 种子（2 正 / 10 负），部署后并入 `.data/gold.jsonl` 扩到 100-200 条 |
| `ai/AGENTS-domain.md` | 领域工作规范摘要（装机后 agent 会话加载） |

**部署门槛**：A0/A1 go + Docker 就绪 + 品牌定稿（禁用 AIHOT 名/Logo）+ taxonomy key 定稿。改动纪律：只落 `industry/` 与新增目录，保持与上游可合并。
