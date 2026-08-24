# 上下文继承与委派边界

## 问题

Parent 知道的状态远多于 Child 完成局部任务所需的状态。全部复制看似保险，却会传递秘密、无关历史、旧假设、恶意指令和不必要的 token；只传一句任务描述则可能丢失验收标准、已有证据和环境约束。

## 主要方案族

### 全历史或同一 Session 继承

Child 继续使用 Parent 的消息历史，状态连续且实现简单。代价是身份和权限边界弱，Child 很难知道哪些历史只是 Parent 的推断。Handoff runtime 常接近这一形状，但可以通过 input filter 改变接收内容。

### 结构化任务包

Parent 生成目标、约束、输入工件、完成标准、已知状态和禁止项。它把委派变成可检查接口，却需要解决压缩遗漏和 schema 过窄。模型生成 packet 时还应区分原始证据与 Parent 判断。

### 共享应用状态或 workspace

Child 不复制全部消息，而是读取应用对象、文件、worktree 或 sandbox snapshot。共享对象适合精确状态，独立 worktree 适合并行代码修改；若写入边界不清，workspace 又会成为隐式全局内存。

### Capability-scoped view

系统按角色、任务和资源生成只读/可写视图，并限制工具、网络、秘密和 memory writer。它把文本过滤扩展到能力隔离，但控制面和调试成本更高。

## 当前研究议程

[When Child Inherits](https://arxiv.org/abs/2605.08460)使 parent-child inheritance 的安全传播成为显式问题。下一步缺少的是可比较的 delegation-completeness 测量：既要知道 Child 是否获得足够信息，也要测量多余状态、攻击内容和 spawn 后陈旧状态。公开 runtime 还需要固定版本检查，区分 session history、application context、workspace snapshot 与 long-term memory 的实际关系。

深入机制见[从复制历史到显式委派契约](context-inheritance/01-mechanisms-and-security.md)。
