# CraftJarvis/JARVIS-1：固定提交工程深潜

**Cluster:** MM-C10  
**Selection:** keep-lineage — Retained for historical/architectural lineage; current trend use is explicitly qualified.

<!-- process:method -->

## 1. 为什么看它，以及不因为什么看它

它由新近性、当前活动、工程表面或历史谱系触发深读；累计 stars 只决定优先检查，不决定技术质量。所有判断固定在下列 commit，且本轮没有安装、测试或 benchmark execution。

<!-- process:limitation -->

## 2. 版本与维护快照

| Field | Observed value |
|---|---|
| Pinned commit | aa9bd97debee045cb35b37564c71dee4c465b9ad |
| Created / pushed | 2023-10-21 / 2024-04-08 |
| Freshness bucket | foundational-lineage |
| Release | none returned / — |
| License | unknown |
| Setup / CI / tests / executed | documented / not-found-in-inspected-tree / present / not-executed |
| 90d commits / contributors | 0 / 0 |
| Single snapshot stars / forks / open issues | 408 / 32 / 7 |
| Engineering surface | thin-surface (3/8) |

这个快照只支持“截至观察时的 repository surface/activity”。单次 stars、commit 数、contributors、open issues、release 或 CI presence 都不能单独推出增长、稳定性、性能或生产采用；PR 合并时延、issue close rate 和 bus factor 本轮没有测量。

<!-- process:limitation -->

## 3. 固定提交架构

这是 2023/2024 Minecraft embodied-agent 研究代码的离线评估快照：multimodal language planner 将视觉/文本指令映射成计划，goal-conditioned STEVE-1/Malmo controller执行；assets/memory.json 是不完整的 fixed memory。README明确 multimodal descriptor/retrieval 与 online growing-memory learning 尚未发布，因此不能把 EpisodeStorage 误称为完整 agent-memory write/index/read系统。

| Component | Responsibility | Fixed-source locator |
|---|---|---|
| multimodal language planner | 接收 visual observation+instruction并生成 Minecraft plan/subgoals | `GR-S027-R` — readmes/GRC027.md abstract/usage |
| fixed memory asset | offline evaluation的静态 memory.json；当前缺少 multimodal state/action sequence及 retrieval implementation | `GR-S027-R` — readmes/GRC027.md lines 89-109; tree jarvis/assets/memory.json |
| STEVE-1/Malmo controller | 把 planner subgoal变成 Minecraft embodied actions/environment interaction | `GR-S027-R` — readmes/GRC027.md related projects; tree jarvis/stark_tech,jarvis/steveI |
| EpisodeStorage | 将训练/轨迹 frames.mp4、actions.pkl、embeds_attn.pkl、metadata.json与len.txt落盘并检查长度 | `GR-S027-T` — jarvis/steveI/steveI_lib/data/EpisodeStorage.py; blob 07052194a97a990bb1b5629cb193c1f932618609; sha256 dfb5f1aef0a26aaa137435a8c7300f70f954d624e7eed6fe2d3a0933d4e3e78d |

这里的 component 关系来自固定 SHA 的代码、manifest 或文档定位；它不是按顶层目录猜架构，也不把 README 的能力宣称提升为运行事实。

## 4. Write → store/index → read → action 数据流

| Step | Operation | From → to | Fixed-source locator |
|---:|---|---|---|
| 1 | 加载 fixed memory asset与模型权重；online write path不适用/未发布 | assets/memory.json/checkpoints → offline evaluator/planner | `GR-S027-R` — README Offline Evaluation/Differences |
| 2 | visual observation+human instruction进入 multimodal planner | Minecraft+user → plan/subgoals | `GR-S027-R` — README Abstract |
| 3 | goal-conditioned controller执行 subgoals并产生 frames/actions/attention embeddings | planner → Minecraft trajectory | `GR-S027-R` — README Abstract/Related Projects |
| 4 | EpisodeStorage可把轨迹分文件保存/再次加载；没有证据表明其在该 SHA 被索引回 fixed memory | trajectory → episode directory | `GR-S027-T` — EpisodeStorage.py append/save_episode/load_* |

## 5. 真实依赖、服务与集成约束

| Dependency / service | Role | Fixed-source locator |
|---|---|---|
| torch 2.2.1 + torchvision 0.17.1 | multimodal/planner/controller model runtime | `GR-S027-T` — pyproject.toml blob 8fefd1bc0673dbf090c560cbfbb6a186e6bf9951; sha256 311e50e1325511637546fed96291d8a562b98dcde30141d90054bfaa53cd14f8 |
| gym 0.23.1 + gymnasium 0.29.1 + Malmo/JDK8 | Minecraft environment/control stack | `GR-S027-R` — README Install Dependencies; pyproject.toml |
| openai 1.16.0 | language-model planner API，需 OPENAI_API_KEY | `GR-S027-T` — pyproject.toml dependencies; README Usage |

**Integration constraints:**

- README明确只发布 offline evaluation；multimodal descriptor、retrieval、learning.py与online growing memory不可用。 (`GR-S027-R` — readmes/GRC027.md lines 68,77-109)
- 项目固定 gym==0.23.1，而 mineclip/minedojo依赖不同版本；README直接提示冲突可能出现。 (`GR-S027-R` — readmes/GRC027.md lines 20-58)
- 需要 JDK8、构建Minecraft/Malmo、下载weights并设置OPENAI_API_KEY，部署成本远高于普通memory library。 (`GR-S027-R` — README Install/Usage)

## 6. 维护、Issue / PR 可见性

- 2026-08-10 观察：rolling90d commits=0、unique contributors=0、open issues snapshot=7；last push 2024-04-08；无release、CI未发现、tests tree存在。 (`GR-S027-O` — observations.jsonl/repositories.jsonl GRC027)
- open issues snapshot=7；PR latency/issue close-time未测，且当前维护者响应未知。 (`GR-S027-O` — observations.jsonl GRC027)

## 7. 项目特定失败模式

| Failure mode | Trigger | Impact | Evidence / inference boundary |
|---|---|---|---|
| memory功能缺失 | 尝试使用online growth或multimodal retrieval | 核心模块未发布，无法完成承诺的增量memory loop | GR-S027-R; inference=false |
| fixed memory信息不全 | 任务依赖被移除的state/action sequence | offline planner缺少演示细节，行为覆盖与论文系统不等价 | GR-S027-R; inference=false |
| environment dependency conflict | gym/mineclip/minedojo/JDK/Malmo版本不兼容 | 环境无法构建或runtime API不匹配 | GR-S027-R, GR-S027-T; inference=true |

## 8. 放回簇内后的设计判断

**本项目要回答的簇级决策：** multimodal/world state 是否保留 observation provenance、visibility、belief 与 action transition。

**首要失败风险：** 状态覆盖、模态错配、不可见区域被当已知和 token/storage 爆炸。

这个判断以第 3–7 节的项目特定 component、flow、dependency、constraint 与 failure records 为基础；它不把项目孤立排名，也不从 stars 或目录存在推导质量。

## 9. 采用边界与仍未知

仅作为 memory-augmented embodied planning 的研究lineage参考；不能作为现成通用memory engine或当前趋势实现。论文/任务成功率未复跑，独立采用未验证。

本轮没有保留独立公开代码引用；这不证明外部采用不存在。

**Unknowns:**

- PR latency 未测
- issue close-time 未测
- 未发布组件是否存在于私有代码未知
- 独立 adoption 未验证
- 无法静态确认fixed memory被哪些路径实际读取

## 10. 可推翻的验证计划

1. 在固定 commit 和记录的 manifest 下重放 setup/tests；失败就把 documented/present 降级为 partial/missing。
2. partial-observation 轨迹中测 state update、historical query、plan translation 和 action success。
3. 固定 model/agent/data/budget，与无 memory、raw context 或同簇替代实现做 matched comparison；同时保存 latency、token、storage、failure 和 security trace。
4. 复核 release migration、issue/PR 维护和至少一个独立部署；没有这些证据就保持 adoption abstention。

## 11. 固定提交原子证据

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

At the 2026-08-10T05:12:54Z GitHub snapshot, CraftJarvis/JARVIS-1 was created 2023-10-21, last pushed 2024-04-08, pinned at aa9bd97debee045cb35b37564c71dee4c465b9ad, had 408 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C027-1 -->

At pinned commit aa9bd97debee045cb35b37564c71dee4c465b9ad, the inspected engineering surface for CraftJarvis/JARVIS-1 was setup=documented, CI=not-found-in-inspected-tree, tests=present, license=unknown, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C027-2 -->

The repository's own GitHub metadata describes CraftJarvis/JARVIS-1 as: “JARVIS-1: Open-world Multi-task Agents with Memory-Augmented Multimodal Language Models”
<!-- claim:GR-C027-3 -->

At pinned commit aa9bd97debee045cb35b37564c71dee4c465b9ad, fixed-source inspection of CraftJarvis/JARVIS-1 supports this project-specific architecture reading: 这是 2023/2024 Minecraft embodied-agent 研究代码的离线评估快照：multimodal language planner 将视觉/文本指令映射成计划，goal-conditioned STEVE-1/Malmo controller执行；assets/memory.json 是不完整的 fixed memory。README明确 multimodal descriptor/retrieval 与 online growing-memory learning 尚未发布，因此不能把 EpisodeStorage 误称为完整 agent-memory write/index/read系统。 The repository was not executed in v09.
<!-- claim:PRJ-A010 -->

At pinned commit aa9bd97debee045cb35b37564c71dee4c465b9ad, CraftJarvis/JARVIS-1 has these inspected dependencies or services: torch 2.2.1 + torchvision 0.17.1: multimodal/planner/controller model runtime; gym 0.23.1 + gymnasium 0.29.1 + Malmo/JDK8: Minecraft environment/control stack; openai 1.16.0: language-model planner API，需 OPENAI_API_KEY. Its recorded integration constraints are: README明确只发布 offline evaluation；multimodal descriptor、retrieval、learning.py与online growing memory不可用。; 项目固定 gym==0.23.1，而 mineclip/minedojo依赖不同版本；README直接提示冲突可能出现。; 需要 JDK8、构建Minecraft/Malmo、下载weights并设置OPENAI_API_KEY，部署成本远高于普通memory library。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I010 -->

At pinned commit aa9bd97debee045cb35b37564c71dee4c465b9ad, the inspected repository tree for CraftJarvis/JARVIS-1 exposed these architecture or integration locations: assets, jarvis, scripts; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C010 -->

At the 2026-08-10T05:12:54Z GitHub/API snapshot for CraftJarvis/JARVIS-1, the inspected rolling-90d window contained 0 commits and 0 unique contributors, while open issues were 7; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M010 -->

<!-- synthesis:PRJ-S10 claims:GR-C027-1,GR-C027-2,GR-C027-3,PRJ-A010,PRJ-I010,PRJ-C010,PRJ-M010 clusters:MM-C10 -->

<!-- process:limitation -->
