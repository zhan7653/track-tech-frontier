# 跨工具与跨 Runtime 协作

多个 coding agent、桌面 Agent、云 Agent 和 MCP/A2A 服务可能围绕同一项目工作。共享文件或 memory service 能让它们交换状态，但不同 runtime 对 Agent identity、session、tool result、workspace、permission 和 long-term memory 的定义并不一致。

跨 runtime 需要解决：稳定主体标识、project/branch scope、schema 与能力协商、来源保留、并发写入、离线同步和删除。把所有工具指向同一 JSON 文件只能建立物理共享，不能自动建立冲突、权限和 commit 语义。

此场景与普通互操作不同：协议不仅传输内容，还要保留“哪个 Agent 在什么权限和任务下产生、是否已经验证、谁可以继续使用”。
