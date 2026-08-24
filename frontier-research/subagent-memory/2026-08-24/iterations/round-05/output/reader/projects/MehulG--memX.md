# memX：Redis LWW + JSON Schema + 进程内 WebSocket Pub/Sub

**固定版本：** [`MehulG/memX@86aeffe`](https://github.com/MehulG/memX/tree/86aeffed547e9978d214f2a101136d955042301f)  
**观察：** 2026-08-24；无 release；MIT；最近 push 2026-01-12，最近90天commit为0。未启动服务。

## 结论

memX是一个小而清晰的 shared typed state service：FastAPI鉴权、Redis authoritative value/schema、server timestamp LWW、JSON Schema和WebSocket通知。它适合共享当前键值，不是完整长期 Memory：没有history、provenance、semantic retrieval、conflict object、forgetting或belief commit。README称 Redis pub/sub，但固定代码的 subscriber registry是进程内 Python dict；多 worker/host通知不会自动共享。

## 写入数据流

```text
POST /set {key,value} + x-api-key
→ Supabase or local ACL lookup
→ optional user_id[:8] namespace prefix
→ JSON Schema validation if schema exists
→ Redis WATCH current key
→ compare server time, MULTI/SET value+ts
→ in-process publish to WebSocket subscribers
```

[`store.set_value`](https://github.com/MehulG/memX/blob/86aeffed547e9978d214f2a101136d955042301f/store.py#L25)用Redis WATCH/MULTI重试并写 `{value, ts}`。timestamp由API进程生成；它实现确定的最后写入值，不保留loser或说明哪个Agent更可信。

## Schema 与 ACL

Schema以 `memx:schema:<key>`存在Redis，Draft7验证发生在写 value前。Supabase `api_keys`可给 read/write glob patterns和 user_id；如果Supabase查询失败，代码回退本地 `config/acl.json`。这便于dev可用性，也意味着本地 key在中心鉴权故障时仍可生效。

带 user_id时真实Redis key使用前8字符prefix；scope检查也对同一prefix执行。它不是 tenant/Agent/project多维 identity，prefix碰撞和 key naming discipline由部署者负责。

## 通知实现

[`pubsub.py`](https://github.com/MehulG/memX/blob/86aeffed547e9978d214f2a101136d955042301f/pubsub.py)维护 `subscriptions[event][key] -> websocket list`，publish逐连接 `send_json`并移除失败socket。没有Redis channel、持久offset、ack、replay或跨process fan-out。WebSocket loop只sleep等待断开；schema和value使用两个event type。

## 依赖、测试与维护

依赖FastAPI、Redis、jsonschema、optional Supabase、requests/websockets SDK、Docker Compose。仓库有SDK tests和smoke/example，但无大量并发/ACL/多worker测试，未见release。单点Stars不用于质量判断。

## 项目特有失败模式

- LWW隐藏语义冲突和stale writer；
- value没有delete/history/audit；
- 进程内subscriber在多worker、restart时丢失；
- Supabase故障回退本地ACL改变控制源；
- first-8 user prefix是弱namespace；
- schema验证结构不验证事实；
- server clocks跨多个API host可能不一致。

它的价值是作为“最小实时共享状态”工程对照：新增治理能力需要明确增加哪些组件，而不能把简单Redis服务误称完整Subagent Memory。
