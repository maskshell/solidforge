---
queue_version: v1
frozen_at: 2026-09-16
plan_ref: docs/product-spec.md
authority_chain:
  - docs/product-spec.md
status: frozen
---

# Plan Queue — product-spec

FROZEN plan interpretation emitted by blueprint-crafting `freeze`. Read-only for the executor; revise only via the Revision Channel (`status` -> `revising` -> edit + queue_version bump -> `status: frozen`). See parallel-development `references/plan-driven-mode.md`.

## Summary (checkpoint view)

16 item(s). DoD source: docs/product-spec.md.

## Items

```json
[
  {
    "item_id": "SPEC-AC-1",
    "seq": 1,
    "depends_on": [],
    "dod_ref": "docs/product-spec.md §6 AC-1",
    "title": "EPUB 导入",
    "scope": "三种途径导入 .epub，解析元数据 3s 内入书架，重复导入合并",
    "source_location": "docs/product-spec.md §6 AC-1",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "SPEC-AC-2",
    "seq": 2,
    "depends_on": [
      "SPEC-AC-1"
    ],
    "dod_ref": "docs/product-spec.md §6 AC-2",
    "title": "TXT 导入",
    "scope": "编码自动检测（UTF-8/GBK/GB18030/UTF-16），50MB 10s 内解析，智能章节切分",
    "source_location": "docs/product-spec.md §6 AC-2",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "SPEC-AC-3",
    "seq": 3,
    "depends_on": [
      "SPEC-AC-1"
    ],
    "dod_ref": "docs/product-spec.md §6 AC-3",
    "title": "MOBI/AZW3 导入转换",
    "scope": "导入时转换为 EPUB 再入库；失败给明确原因且保留原文件",
    "source_location": "docs/product-spec.md §6 AC-3",
    "open_decisions": [
      {
        "id": "ODP-4",
        "kind": "deferred"
      }
    ],
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "SPEC-AC-4",
    "seq": 4,
    "depends_on": [
      "SPEC-AC-1",
      "SPEC-AC-10"
    ],
    "dod_ref": "docs/product-spec.md §6 AC-4",
    "title": "书架管理",
    "scope": "搜索/分组/排序/删除；删除默认保留笔记直至用户确认清除",
    "source_location": "docs/product-spec.md §6 AC-4",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "SPEC-AC-5",
    "seq": 5,
    "depends_on": [
      "SPEC-AC-1"
    ],
    "dod_ref": "docs/product-spec.md §6 AC-5",
    "title": "续读恢复",
    "scope": "重开书定位到上次位置：EPUB 段落级 CFI，TXT 字符偏移 ±50",
    "source_location": "docs/product-spec.md §6 AC-5",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "SPEC-AC-6",
    "seq": 6,
    "depends_on": [
      "SPEC-AC-5"
    ],
    "dod_ref": "docs/product-spec.md §6 AC-6",
    "title": "排版定制实时生效",
    "scope": "字号/行距/边距/字体调整 200ms 内重排；满足 OM-4 中文排版质量",
    "source_location": "docs/product-spec.md §6 AC-6",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "SPEC-AC-7",
    "seq": 7,
    "depends_on": [
      "SPEC-AC-6"
    ],
    "dod_ref": "docs/product-spec.md §6 AC-7",
    "title": "主题系统",
    "scope": "白/米黄/深黑三档 + 自定义颜色；深色模式跟随系统免重启",
    "source_location": "docs/product-spec.md §6 AC-7",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "SPEC-AC-8",
    "seq": 8,
    "depends_on": [
      "SPEC-AC-6"
    ],
    "dod_ref": "docs/product-spec.md §6 AC-8",
    "title": "双翻页模式",
    "scope": "上下滚动与左右翻页可切换且保持位置；无白屏闪烁（OM-3）",
    "source_location": "docs/product-spec.md §6 AC-8",
    "open_decisions": [
      {
        "id": "ODP-1",
        "kind": "deferred"
      }
    ],
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "SPEC-AC-9",
    "seq": 9,
    "depends_on": [
      "SPEC-AC-5"
    ],
    "dod_ref": "docs/product-spec.md §6 AC-9",
    "title": "阅读控制层",
    "scope": "点按中央呼出/隐藏控制层（进度/目录/设置/书内搜索）；点按两侧翻页",
    "source_location": "docs/product-spec.md §6 AC-9",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "SPEC-AC-10",
    "seq": 10,
    "depends_on": [
      "SPEC-AC-5"
    ],
    "dod_ref": "docs/product-spec.md §6 AC-10",
    "title": "高亮与批注",
    "scope": "选中文本 ≥3 色高亮 + 批注；跨重启保留；排版变化后仍正确定位",
    "source_location": "docs/product-spec.md §6 AC-10",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "SPEC-AC-11",
    "seq": 11,
    "depends_on": [
      "SPEC-AC-10"
    ],
    "dod_ref": "docs/product-spec.md §6 AC-11",
    "title": "笔记 Markdown 导出",
    "scope": "全书高亮批注一键导出 Markdown（书名/作者/章节/原文/批注/定位），系统分享导出；OM-5 字段完整率 100%",
    "source_location": "docs/product-spec.md §6 AC-11",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "SPEC-AC-12",
    "seq": 12,
    "depends_on": [
      "SPEC-AC-5",
      "SPEC-AC-10"
    ],
    "dod_ref": "docs/product-spec.md §6 AC-12",
    "title": "iCloud 同步",
    "scope": "两设备进度/高亮/批注经 CloudKit 同步，刷新后一致（OM-6）；冲突最新时间戳胜出（落败写入不计入 OM-7 丢失）；iCloud 不可用时本地完全可用（C4）；正确性以 A4 同书同副本为前提",
    "source_location": "docs/product-spec.md §6 AC-12",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "SPEC-AC-13",
    "seq": 13,
    "depends_on": [
      "SPEC-AC-10"
    ],
    "dod_ref": "docs/product-spec.md §6 AC-13",
    "title": "划词翻译",
    "scope": "选中文本翻译；无 key 跳配置引导而非报错；无 key 且 iCloud 关闭时应用外发请求为 0（OM-8）；译文与原文对照（BYOK，D6）",
    "source_location": "docs/product-spec.md §6 AC-13",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "SPEC-AC-14",
    "seq": 14,
    "depends_on": [
      "SPEC-AC-8"
    ],
    "dod_ref": "docs/product-spec.md §6 AC-14",
    "title": "TTS 听书",
    "scope": "当前页起读，页尾自动翻页/下滚；暂停/继续/停止，语速可调",
    "source_location": "docs/product-spec.md §6 AC-14",
    "open_decisions": [
      {
        "id": "ODP-2",
        "kind": "deferred"
      }
    ],
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "SPEC-AC-15",
    "seq": 15,
    "depends_on": [
      "SPEC-AC-5"
    ],
    "dod_ref": "docs/product-spec.md §6 AC-15",
    "title": "章节摘要",
    "scope": "当前章节生成摘要；无 key/网络失败给可理解提示，不影响主流程（A2 降级）",
    "source_location": "docs/product-spec.md §6 AC-15",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "SPEC-AC-16",
    "seq": 16,
    "depends_on": [
      "SPEC-AC-5"
    ],
    "dod_ref": "docs/product-spec.md §6 AC-16",
    "title": "启动性能门槛",
    "scope": "冷启动到恢复上次阅读位置 ≤2.5s（OM-1；书库 ≥100 本）",
    "source_location": "docs/product-spec.md §6 AC-16",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  }
]
```
