# 最终验证记录

**证据截止：** 2026-08-24  
**验证时间：** 2026-08-24（Asia/Hong_Kong）

## 完成量

| 项目 | 数量 |
|---|---:|
| discovery occurrences | 6,898 |
| canonical entities | 4,298 |
| queries | 109 |
| mapped + deep-verified entities | 207 |
| deep papers / repositories | 42 / 10 |
| sources / claims / evidence | 52 / 56 / 56 |
| syntheses / relations / trend metrics | 10 / 8 / 10 |
| manifested deliverables | 30 |
| substantive iterations | 8 |

## 验证命令与结果

```text
python scripts/research_bundle.py validate --root frontier-research/subagent-memory/2026-08-24
OK: bundle is valid

python scripts/research_bundle.py validate --root frontier-research/subagent-memory/2026-08-24 --strict
OK: bundle is valid

python scripts/validate_reader_suite.py --root frontier-research/subagent-memory/2026-08-24
OK: reader suite is structurally complete

python -m unittest discover -s scripts -p test_*.py
Ran 115 tests
OK
```

Strict validation 仍输出 advisory：未提供可选 coverage-proofs，部分历史/相邻 lane/window cell 保持 partial/not-applicable，且没有为每个 lane/window/perspective 单独声明饱和。这些不是隐藏失败；cluster-level 结构饱和、deep dive、公开 gap 与目标完成均已通过严格校验。

## 需求逐条映射

- 广泛输入：arXiv、Crossref、GitHub Search、GitHub REST、official/web discovery；失败路线保留。
- 先广后深：4,298 entity → 207 mapped/deep → 42 PDF + 10 fixed repository。
- 主报告是地图：overview/architecture/solution landscape；相邻技术略写。
- 分支深入：八个 entry + 八个 mechanism deep page。
- GitHub 工程：十个项目有 pinned commit、数据流、依赖、维护与失败模式。
- 最新趋势：12m/90d window、fixed activity snapshot、主流/前沿分层。
- 人工评审：完整正文之后只保留业务判断与继续深挖事项。
- 不给建议：报告描述方案、条件和边界，不输出产品/架构推荐。
- 5–10 轮迭代：八轮均保存输入、输出快照、差异、问题和基准评估。
