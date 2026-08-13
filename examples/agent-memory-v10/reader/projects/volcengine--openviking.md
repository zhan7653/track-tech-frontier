# OpenViking：把资源、记忆与技能放入同一分层空间

[volcengine/OpenViking](https://github.com/volcengine/OpenViking) 不把 Memory 限定为一组短文本。它将资源、会话提炼出的记忆和技能统一为 `viking://` 虚拟文件系统：内容在一个可导航的层级中，索引只保存 URI、向量与元数据。这是“权威内容—派生语义索引”分离的鲜明工程例子。

**固定观察。** 检查提交为 [`7f6085a`](https://github.com/volcengine/OpenViking/tree/7f6085a2f95c8a79ec4eb82f973cae57628341a9)。仓库 2026-01-05 创建，快照时最新 push 为 2026-08-10、release 为 `python-sdk@0.1.7`；滚动 90 天可见 862 次提交和 102 位贡献者。其 AGPL-3.0 许可证、CI 和测试路径是明确的部署边界；28,136 stars 只是单次关注度快照。

## 这套系统怎样分层

文档的[架构说明](https://github.com/volcengine/OpenViking/blob/7f6085a2f95c8a79ec4eb82f973cae57628341a9/docs/en/concepts/01-architecture.md)将 Client/Service 同时暴露给嵌入式、CLI 和 HTTP 使用者。Parser 与 TreeBuilder 把 PDF、网页、代码等输入组成树；SemanticQueue 在后台自底向上生成 L0/L1/L2 语义表示。AGFS 保存完整内容、多媒体和关系，Vector Index 则保存指向 AGFS 的 URI、向量与 metadata。会话路径由 SessionCompressorV2 归档并抽取 self、peer、experience memory；查询路径由 IntentAnalyzer、HierarchicalRetriever 和 reranker 协作。

这种关系意味着“能找到索引”与“能读到正确内容”是两个层。它能把大型资源、记忆和技能放在同一检索语言下，也需要处理两个层的同步。

## 从输入到使用的数据流

1. 文件资源经 Parser 处理，或对话在 session commit 时归档成批次。
2. TreeBuilder 将资源树写入 AGFS，并将语义工作投给 SemanticQueue。
3. 队列生成分层摘要/表示；会话压缩器按 schema 抽取长期或执行性记忆。索引只写 URI、vector、metadata，不复制全部内容。
4. 查询先做 intent 判断，再进行优先队列式的层级检索与 rerank，最后按 URI 从 AGFS 逐层取回并组装上下文。

会话提炼路径可从[设计文档](https://github.com/volcengine/OpenViking/blob/7f6085a2f95c8a79ec4eb82f973cae57628341a9/docs/design/session-memory-extraction-flow.md)看到；其余流程由同一固定版本的架构文档和源码树支持。本研究未运行队列或服务，因此没有把设计描述改写为吞吐或可靠性结论。

## 服务依赖与集成约束

[`pyproject.toml`](https://github.com/volcengine/OpenViking/blob/7f6085a2f95c8a79ec4eb82f973cae57628341a9/pyproject.toml) 中有 FastAPI/Uvicorn/httpx、SDK，以及 OpenAI/LiteLLM/Volcengine 等模型接口；解析侧依赖 pdfplumber、trafilatura、scrapy、python-docx、openpyxl 和 tree-sitter 家族。它可以是嵌入式库，也可以作为 HTTP 服务运行，但并非没有外部服务假设的轻量本地库。

`add_resource` 之后的语义处理是异步的：调用方要么等待 `wait_processed`，要么接受短时间内内容已存在但语义召回尚不可用。self/peer 路由还依赖 `memory_policy`、schema stage、`peer_enabled` 和安全的 `peer_id`；这些字段传错会改变写入空间。AGPL-3.0 对修改后的服务分发有额外约束，需与技术接口分开考虑。

## 最有代表性的风险

**队列滞后。** Provider 不可用、积压或 worker 中断时，AGFS 已有资源而 L0/L1/vector 尚未形成，读时会漏掉刚写入内容。

**双层漂移。** AGFS 修改与向量索引更新若不同步，URI 可能指向旧内容或缺失内容；反过来，内容存在却不可检索。这是从其双层设计推得的风险，未在本研究中注入故障验证。

**peer 路由错误。** 多条件 policy 组合若错误，记忆可能写错空间或根本未写入。这里的关键不是“是否有图/向量”，而是身份与共享边界能否贯穿异步工作流。

## 维护与尚未知道的事

可见活动、release、测试和 CI 很强，但快照中的 455 个 open issue 不解释支持质量；PR 时延、队列持久化/重试 SLO、迁移过程和独立部署都没有核实。官方 Studio、托管能力和 README benchmark 属项目方的产品/陈述边界，不能据此判断固定 OSS 提交的生产表现。

**证据边界。** 以上是提交 `7f6085a` 的静态源码与文档检查，加 2026-08-10 仓库快照；未运行 embedded、HTTP server 或 migration。
