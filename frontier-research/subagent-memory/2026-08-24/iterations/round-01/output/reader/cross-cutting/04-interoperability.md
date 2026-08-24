# 互操作与集成

Runtime session、application context、handoff item、A2A message、MCP resource/tool、workspace snapshot、checkpoint 和 memory record 位于不同层。它们都能携带状态，却没有相同的持久性、主体、权限和提交语义。

真正的 Subagent Memory 互操作需要稳定 Agent/Task/Project identity、scope mapping、record/patch/artifact schema、capability negotiation、provenance、version、delete/revoke 和 error semantics。一个 API 能跨框架调用，只能证明 transport compatibility，不能证明 memory round-trip 或一致性。
