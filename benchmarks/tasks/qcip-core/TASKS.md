# 四个具体家族与最终证明义务

**整理端文档。以下极性和见证不得出现在 agent 提示中。所有目标均未证明。** 实现体和调用者共同冻结；`tasks.json` 将每个任务绑定到入口、命题及哈希。本轮不声称源程序与派生程序等价。

**v0.2：每个上下文有Lean、原生Rocq、CompCert三版。** 三平台对应目标见[THREE-PLATFORM.md](THREE-PLATFORM.md)与[three-platform.json](three-platform.json)。CompCert当前规范目标位于`compcert/`，使用实际已导出并检查的3.17 AST；旧`rocq/`是v0.1未检查的3.16设计记录。构造中可带版本日志修改实现及任务，冻结后求解者不可修改。最终命题在构造阶段暂不要求证明。

## 共同的执行与定理接口

每份程序提供 `int main(void)`、`int eb_input[8192]` 和 `int eb_output[8192]`。`main` 不接触外部 I/O，不调用 malloc/free 或未给定的外部函数。输入是 typed input 经 `Domain.v` 序列化并补零的 8192 个有符号 32 位整数；初始关系从各自标准 Clight 初始内存出发，把同一个编码写入各自 `eb_input`。arena、scratch、指针地址、队列内部数组不属于观察。

所有入口首先清零输出数组。`eb_output[0]` 是有效 payload 字数，其后为 payload，未用部分全为零。比较 `(main 返回值, 全部8192个输出字)`，因此同时比较长度和内容；填充不泄露内部内存。每份程序正常返回 0。目标不允许仅比较返回 0 而忽略输出。

令 `Run(P,x,o)` 表示 `Execution.run P (encode x) o`：从正确初始化并写入输入后的状态出发，没有可达 stuck 状态，存在无事件的有限 Clight 执行，终止并投影为 `o`。v0.2采用CompCert3.17的`Clight.step2`，使用`clightgen -clight -normalize`。完整语义以[Execution.v](compcert/Execution.v)为准；接口与目标已用Rocq9.2完成类型检查，未证明最终命题。

```coq
Equivalent valid encode A B :=
  forall x, valid x -> exists o,
    run A (encode x) o /\ run B (encode x) o.

Counterexample valid encode A B :=
  exists x oa ob, valid x /\
    run A (encode x) oa /\ run B (encode x) ob /\ oa <> ob.

Certificate valid encode A B :=
  Equivalent valid encode A B \/ Counterexample valid encode A B.
```

公开目标一律是 `Certificate`，不给极性。整理端另外固定下述预期分支。发现安全有限差异才可证明反例；崩溃、越界、超时或内部不变量损坏本身不构成这里的反例。`Equivalent` 还要求所有有效输入上两边安全终止，不是“若两边返回则相同”的部分正确性。

## C-BST：三种删除实现的 map 轨迹

**固定实现。** [bst/body.h](bst/body.h) 中 `V0` 为 QCIP 风格的递归删除及递归 predecessor cursor 搜索，复制前驱的 key/value；`V1` 为 pointer-to-pointer 迭代搜索并移植 successor 节点；`V2` 为移植 VST 思路的 `erase → pushdown_left → turn_left`，通过旋转下推待删除节点。`V3` 与 `V0` 仅差前驱复制时省略 value 赋值。四个 [v0.c](bst/v0.c) / [v1.c](bst/v1.c) / [v2.c](bst/v2.c) / [v3.c](bst/v3.c) 入口固定宏，不允许模型改宏。

**输入域。** `BST.input` 包含 0–32 个初始 `(key,value)` 和 0–64 条 `Delete key` / `Lookup key`。初始 key 两两不同；所有 key∈[-1024,1024]、value∈[-1000000,1000000]。以输入顺序调用同一个普通 BST 插入器构造初始树：不局限于平衡形状，任意≤32节点 BST 都可由相应插入顺序覆盖。允许空树、删除不存在的键、重复删除及任意有效查询；不接受外部内部节点句柄。

**编码。** `[n,q] ++ 初始key/value对 ++ [opcode,key]序列 ++ 零填充`，删除 opcode=0、查询=1。所有实现得到相同初始插入顺序和命令序列，但删除后形状不必相同。32 节点 arena 分配只在初始化发生；删除调用可见 `retire` 标记，不释放也不复用节点。

**观察。** 每次删除输出 `[0,0]`（void 操作的固定完成标记）；查询输出 `[1,found,value]`，缺失为 `[1,0,0]`，值为 0 仍可与缺失区分。最后输出 `[-2] ++ 最终树中序key/value对`。中序投影暴露最终 map 内容，不暴露 root、拓扑或物理节点身份；它是固定的读出代码，不是独立的删除正确性规约。

**调用与难度。** `main → erase → get_pre/erase` 或 `main → erase → pushdown_left → turn_left`；还包括初始化、查询和递归读出。SUCCESSOR 暂标 L3，ROTATE 暂标 L4；等级须在参考证明阶段校准。

| 任务 | 实现对 | 整理端待证明定理 |
|---|---|---|
| C-BST-SUCCESSOR | V0 / V1 | `C_BST_SUCCESSOR : Equivalent BST.valid BST.encode impl_BST_V0 impl_BST_V1` |
| C-BST-ROTATE | V0 / V2 | `C_BST_ROTATE : Equivalent BST.valid BST.encode impl_BST_V0 impl_BST_V2` |
| C-BST-VALUE | V0 / V3 | `C_BST_VALUE : Counterexample BST.valid BST.encode impl_BST_V0 impl_BST_V3` |

**反例任务。** 初始 `[(2,20),(1,10),(3,30)]`，执行 `Delete 2; Lookup 1`。候选差异是查询 value=10 与 20，且最终投影不同；两边预期均安全终止。不能用只比较 membership 的弱观察掩盖该错误。该种子已作 native 检查，Rocq 证书尚未构造。

**最终目标文件：** [BSTExpected.v](rocq/BSTExpected.v) 和 [BSTCertificates.v](rocq/BSTCertificates.v)。

## C-AVL：递归、显式祖先栈与旋转调用分解

**固定实现。** [avl/body.h](avl/body.h) 中 `V0` 保留 QCIP 的递归 `insert → update_height/balance → rotate_lr/rotate_rl → rotate_left/rotate_right → update_height`；`V1` 用显式 `node **path[64]` 保存祖先位置并反向更新和平衡；`V2` 保留递归插入，将双旋的两次单旋直接放入 `balance`，改变调用分解。`V3` 在左旋时把应转移的中间子树设为 null。该变异会丢失可查询键，不只是破坏隐藏平衡性。

**输入域。** `AVL.input` 为从空树开始的 0–64 条 `Insert key value` / `Lookup key`。key、value 界同 BST；重复插入**忽略新 value**，与 QCIP demo 的政策一致。查询值不受插入是否发生限制。至多64次插入，因此64节点 arena 足够；高度字段保留 unsigned char，64节点路径也不会超出255。显式祖先栈不做堆分配。高度、容量和旋转安全性仍是待证义务，未从测试推出。

**编码。** `[q] ++ [opcode,key,value]序列 ++ 零填充`。插入 opcode=0；查询=1且 value槽固定0。`new_node`、高度计算和两种单旋的体全部可见且固定。

**观察。** 插入输出 `[0,0]` 固定完成标记；查询输出 `[1,found,value]`；最后 `[-2] ++ 中序key/value对`。不比较 shape、高度、旋转次数、栈使用量和分配地址。不声称两边都满足一个独立 AVL/map 功能规约。STACK 暂标 L4；FACTOR 是相同算法的调用分解对照，暂标 L2，不能仅因函数多就标最难。

| 任务 | 实现对 | 整理端待证明定理 |
|---|---|---|
| C-AVL-STACK | V0 / V1 | `C_AVL_STACK : Equivalent AVL.valid AVL.encode impl_AVL_V0 impl_AVL_V1` |
| C-AVL-FACTOR | V0 / V2 | `C_AVL_FACTOR : Equivalent AVL.valid AVL.encode impl_AVL_V0 impl_AVL_V2` |
| C-AVL-MIDDLE | V0 / V3 | `C_AVL_MIDDLE : Counterexample AVL.valid AVL.encode impl_AVL_V0 impl_AVL_V3` |

**反例任务。** 依次插入 `(1,10),(0,0),(3,30),(2,20),(4,40),(5,50)`，再 `Lookup 2`。候选差异为 `(found,value)=(1,20)` 与 `(0,0)`；中间子树在最终左旋时丢失。种子轨迹发现难度暂标 W2；不能保留先前仅凭源复杂度给出的 W3 标签。

**最终目标文件：** [AVLExpected.v](rocq/AVLExpected.v) 和 [AVLCertificates.v](rocq/AVLCertificates.v)。

## C-RING：跨界复制与状态表示替换

**固定实现。** [ring/body.h](ring/body.h) 中 `V0` 使用 read/write index、full flag 和至多两段 copy；`V1` 使用相同 flag 表示，逐字节取模复制；`V2` 改为 occupancy count、逐字节复制；`V3` 在计算占用长度时省略“read=write且full表示满”的分支。复制函数是可见循环，没有依赖未提供的 memcpy 合约。

**输入域。** `Ring.input` 包含容量 1–64 和 0–64 条 `Write bytes`、`Read n`、`Force bytes`。每次请求长度1–capacity，每个 byte∈[0,255]。从空缓冲区和已初始化零字节存储开始；允许读空、写满、截断、绕回、覆盖和多轮交替。调用者 src/dst 是不同的局部64字节数组，与 ring.data 不重叠；没有 NULL 输入或长度0。

**固定 API 行为边界。** 普通 write 最多接收空闲空间；read 最多交付已有字节；force 请求长度≤capacity，先丢弃恰好足够的最旧字节，再接收全部请求。无字节完成时 code=1、actual=0；其余 code=0、actual为完成字节数。原 QCIP/XiZi read 返回 EOK/ERROR，本任务**显式扩展 actual-count 输出并统一派生 API**，不能描述为不变的原始 CRTOS 接口。返回约定由实现代码固定，不给独立 FIFO 功能后置条件。

**编码。** `[capacity,q] ++ 每条66字record ++ 零填充`。record为 `[opcode,length,64字payload]`；write=0、read=1、force=2。read payload全0；write/force payload有效字节后补0。

**观察。** 每条操作输出 `[opcode,code,actual]`，read再附交付的actual个字节。最后 `[-2,remaining_count] ++ 从read index开始的逻辑顺序字节`。不比较index、full/count、已消费字节的物理残留或scratch。COPY 暂标 L2–L3，REP 暂标 L3。所有中间 read 的内容都被观察，不能仅比较最终缓冲区。

| 任务 | 实现对 | 整理端待证明定理 |
|---|---|---|
| C-RING-COPY | V0 / V1 | `C_RING_COPY : Equivalent Ring.valid Ring.encode impl_RING_V0 impl_RING_V1` |
| C-RING-REP | V0 / V2 | `C_RING_REP : Equivalent Ring.valid Ring.encode impl_RING_V0 impl_RING_V2` |
| C-RING-FULL | V0 / V3 | `C_RING_FULL : Counterexample Ring.valid Ring.encode impl_RING_V0 impl_RING_V3` |

**反例任务。** capacity=2，`Write [17,29]; Read 2`。正常实现返回成功、actual=2、交付 `[17,29]`；变异实现把已满状态视为空，返回code=1、actual=0。两边均不越界。此任务的短种子暂标 W1；较长交错覆盖反例另建上下文，不能把它算作当前已实现任务。

**最终目标文件：** [RINGExpected.v](rocq/RINGExpected.v) 和 [RINGCertificates.v](rocq/RINGCertificates.v)。

## C-DIJK：图 client 与可替换最小优先队列

**固定实现。** [dijkstra/body.h](dijkstra/body.h) 与 [dijkstra/queue.h](dijkstra/queue.h) 中 `V0` 为 QCIP forward-star client + 有序数组最小队列，保留 stale-entry 判断和溢出保护；`V1` 不建队列，扫描未settled顶点选最小距离；`V2` 保留队列 client、替换为二叉最小堆；`V3` 在 relax 中额外要求 `dist[v]==INF`，只接受首次发现的距离。V0、V2、V3 的 queue_clear/empty/push/pop 都有可见体。源算法跨文件调用；派生构建将 client/provider 包含在同一翻译单元，不冒充已经完成分离链接语义。

**输入域。** `Dijkstra.input` 为1–10个顶点、0–64条有向边、合法源点。端点∈[0,n)，权重∈[0,1000]；允许自环、平行边、0权边、环、不可达点和相同最短距离。输入为有序边列表，固定 builder 按输入次序头插生成 forward-star，邻接链安全性来自同一可见 builder，而不是要求模型猜一个外部图布局。

**整数和容量边界。** `INF=1000000000`，正队列实现容量641。n≤10、w≤1000使存在的最短路径可选简单路径、距离≤9000，与INF不碰撞；计算溢出和队列占用界仍须在形式化执行证明中建立。容量641用于容纳拟采用的 `1+n*m` 保守界（最多641），该界是**待证内部引理**，不是有效输入前提，也不是现成证书。不得用“队列空间足够”作为循环定义的外部保证。

**编码。** `[n,m,source] ++ [from,to,weight]边序列 ++ 零填充`。`build_graph → solve → queue_*` 调用均冻结。全局scratch初始化由driver/solve完成，不读取先前一次native运行的残留。

**观察。** 输出长度n、按顶点编号排列的完整dist向量，INF表示不可达。保留main返回0；不观察队列顺序、同距离的出队次序、settled次序或前驱选择。不存在要求每个实现满足的独立 shortest-path 规约。SCAN 暂标 L4，HEAP 暂标 L3–L4。

| 任务 | 实现对 | 整理端待证明定理 |
|---|---|---|
| C-DIJK-SCAN | V0 / V1 | `C_DIJK_SCAN : Equivalent Dijkstra.valid Dijkstra.encode impl_DIJKSTRA_V0 impl_DIJKSTRA_V1` |
| C-DIJK-HEAP | V0 / V2 | `C_DIJK_HEAP : Equivalent Dijkstra.valid Dijkstra.encode impl_DIJKSTRA_V0 impl_DIJKSTRA_V2` |
| C-DIJK-SEEN | V0 / V3 | `C_DIJK_SEEN : Counterexample Dijkstra.valid Dijkstra.encode impl_DIJKSTRA_V0 impl_DIJKSTRA_V3` |

**反例任务。** n=3、source=0，按顺序给边 `(0,1,10),(0,2,1),(2,1,1)`。候选观察为 `[0,2,1]` 与 `[0,10,1]`。首次入队后仍需允许改善距离，不能把“已经发现”当作“最终确定”。安全有限执行与输出差异都要成为反例定理的组成部分。暂标 W2。

**最终目标文件：** [DIJKSTRAExpected.v](rocq/DIJKSTRAExpected.v) 和 [DIJKSTRACertificates.v](rocq/DIJKSTRACertificates.v)。

## 完成度与下一关

四家族均完成源级调用闭包和具体目标设计；12条预期分支只是整理假设，须以之后的参考证书确认。有限 native 检查共660个家族输入、每个跑4实现，即2640次程序执行；每个家族包括边界case、候选反例和160个固定种子随机输入。三个正向实现的观察在这些输入上吻合，四个反例种子观察有差异，ASan/UBSan未报错。这不能支持全域安全或“已证实标签”的结论。

下一关依次是固定CompCert环境、导出并审计16个AST、类型检查域与目标、冻结AST哈希；**证明阶段仍暂停**。之后得到八个全称等价参考证明与四个反例参考证书，才可标记reference-ready。不得把今天的2640次有限执行记为benchmark的形式化求解数。
