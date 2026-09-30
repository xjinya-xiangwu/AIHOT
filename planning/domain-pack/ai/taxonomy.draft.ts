// AI Domain Pack · taxonomy 初稿（D12 窄化版，2026-09-30）
// 部署时替换 industry/taxonomy.ts。注意：CATEGORIES.key 进 URL，上线后不可改——上线前定稿。
// 模型按这里的词表打标签；主题页 topics.json 按标签归类；筛选栏按类别分组（未来角色分榜 = category+topics 组合）。

export const CATEGORIES = [
  { key: "models", label: "模型", section: "模型动态", guide: "模型发布/降价/能力变化/开源权重/评测结论——影响『换模型』决策（含闭源 API 与开源权重）" },
  { key: "environment", label: "环境", section: "harness 与工具", guide: "agent harness 本体（Claude Code/Codex/Cursor/ZCode 等）与运行/部署/编排工具的发布与重要更新——影响『用什么干活』" },
  { key: "skills", label: "技能", section: "skills·插件·MCP", guide: "能更好完成某任务的新 skills/插件/MCP server，及'该删什么'的 context 成本讨论——影响『装什么/删什么』" },
  { key: "compute", label: "算力", section: "算力与成本", guide: "API 定价变动、tokens 中转站、算力平台与免费额度——影响『迁去哪』" },
  { key: "discussion", label: "讨论", section: "实践与讨论", guide: "高价值实践帖/实测/踩坑——必须直接服务于上述四类的使用决策，泛观点剔除" },
] as const;

export const ITEM_TYPES = [
  "model_release", "price_change", "open_model", "harness_tool", "skill_plugin", "mcp_server", "compute_offer", "practice_review",
] as const;

export const CATEGORY_TAGS = [
  "模型动态", "价格变动", "开源模型", "harness/工具", "skills/插件", "MCP", "算力/中转", "额度/免费", "实践/评测", "其他",
] as const;

export const TOPIC_TAGS = [
  "Claude Code", "Codex", "Cursor", "ZCode", "Hugging Face", "OpenRouter", "Ollama", "Agent编排", "Context管理", "本地部署",
] as const;

export const ENTITY_TAGS = [
  "Anthropic", "OpenAI", "DeepSeek", "智谱", "千问", "Meta", "xAI", "Hugging Face", "OpenRouter", "GitHub", "Cursor", "Ollama", "Civitai",
] as const;

export const TAG_SYNONYMS: Readonly<Record<string, string>> = {
  模型: "模型动态", 发布: "模型动态", 降价: "价格变动", 定价: "价格变动", api: "价格变动",
  开源: "开源模型", 权重: "开源模型", 插件: "skills/插件", 技能: "skills/插件", 扩展: "skills/插件",
  中转: "算力/中转", 中转站: "算力/中转", 羊毛: "额度/免费", 免费: "额度/免费", 白嫖: "额度/免费",
  harness: "harness/工具", agent工具: "harness/工具", 编排: "Agent编排", 上下文: "Context管理",
};

export const CATEGORY_BY_ITEM_TYPE: Readonly<Record<string, string>> = {
  model_release: "模型动态", price_change: "价格变动", open_model: "开源模型", harness_tool: "harness/工具",
  skill_plugin: "skills/插件", mcp_server: "MCP", compute_offer: "算力/中转", practice_review: "实践/评测",
};

export const ENTITIES: Record<string, { name: string; displayTag: string | null; aliases: string[] }> = {
  anthropic: { name: "Anthropic", displayTag: "Anthropic", aliases: ["Anthropic", "Claude", "Opus", "Sonnet"] },
  openai: { name: "OpenAI", displayTag: "OpenAI", aliases: ["OpenAI", "ChatGPT", "Codex", "GPT"] },
  deepseek: { name: "DeepSeek", displayTag: null, aliases: ["DeepSeek", "深度求索"] },
  zhipu: { name: "智谱 GLM", displayTag: null, aliases: ["智谱", "GLM", "Z.ai"] },
  qwen: { name: "千问 Qwen", displayTag: null, aliases: ["Qwen", "通义", "千问"] },
  meta: { name: "Meta", displayTag: "Meta", aliases: ["Meta", "Llama"] },
  xai: { name: "xAI", displayTag: "xAI", aliases: ["xAI", "Grok"] },
  "hugging-face": { name: "Hugging Face", displayTag: "Hugging Face", aliases: ["Hugging Face", "HF"] },
  openrouter: { name: "OpenRouter", displayTag: null, aliases: ["OpenRouter"] },
  cursor: { name: "Cursor", displayTag: null, aliases: ["Cursor", "Anysphere"] },
  ollama: { name: "Ollama", displayTag: null, aliases: ["Ollama"] },
  civitai: { name: "Civitai", displayTag: null, aliases: ["Civitai"] },
};

export const IDENTITY_LEXICON: ReadonlyArray<{ id: string; name: string; patterns: RegExp[] }> = [
  { id: "anthropic", name: "Anthropic", patterns: [/anthropic|\bclaude\b/i, /\b(?:opus|sonnet|haiku)\s*\d+(?:[.\-]\d+)*\b/i] },
  { id: "openai", name: "OpenAI", patterns: [/openai|chatgpt|\bgpt-?[o\d]|\bcodex\b/i] },
  { id: "deepseek", name: "DeepSeek", patterns: [/deepseek|深度求索/i] },
  { id: "zhipu", name: "智谱 GLM", patterns: [/智谱|\bglm-?[0-9]/i] },
  { id: "qwen", name: "千问 Qwen", patterns: [/\bqwen|通义|千问/i] },
  { id: "xai", name: "xAI", patterns: [/\bxai\b|\bgrok\b/i] },
  { id: "cursor", name: "Cursor", patterns: [/\bcursor\b/i] },
  { id: "ollama", name: "Ollama", patterns: [/\bollama\b/i] },
  { id: "hugging-face", name: "Hugging Face", patterns: [/hugging\s?face/i] },
];

export const PUBLISHER_DOMAINS: Readonly<Record<string, string>> = {
  "anthropic.com": "anthropic", "openai.com": "openai", "deepseek.com": "deepseek",
  "z.ai": "zhipu", "qwenlm.github.io": "qwen", "ai.meta.com": "meta",
  "huggingface.co": "hugging-face", "openrouter.ai": "openrouter", "github.blog": "github",
};
