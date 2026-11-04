# 三组状态程序的具体比较边界与目标

每题给定两个不可修改实现，提供两个独立命题分支：全域等价，或专门化到字面量输入及两边观察的反例。预期极性只用于构造端。所有最终关系命题保持未证明。

输入为整数列表。C把相同字段补零放入8192字全局输入，观察main返回0与初始化的完整输出global；原生观察为`Some (length :: payload)`。以下描述payload，省略长度头和C输出零填充。两次失败或两个`None`不算等价。所写行为用于解释固定代码，不另定义第三份正确结果oracle。

## S-FRAME 增量分帧与残留存储

输入`[q] ++ q条[op,len,b0,...,b7]`，0≤q≤64。op=0 feed、1 finish、2 reset。feed长度0–8，前len字节0–255，未用字节必须0；非feed的len和全部字节为0。**错误帧、不完整帧、空feed、错误后的后续操作均合法。**

私有帧编码为`[tag,len,payload...,checksum]`，tag为1–3，帧payload长度0–8，checksum是头及payload异或。处理顺序：有残留时先查tag（错误1，位置为残留开头），至少两字节后查长度（错误2，位置为长度字节），等完整帧后查checksum（错误3，位置为checksum）。不完整且未finish时保留残留。finish对非空无错误残留产生错误4，位置为残留开头；对空状态成功。错误为sticky，后续feed忽略全部新字节，finish不改变该错误；reset清空残留、消耗计数和错误。成功finish不关闭对象，后续feed仍可继续。

每条命令观察：

```text
[op,code,errorPosition,consumed,frameCount]
++ frameCount条[tag,len,payload...]
++ [pendingLen] ++ pendingBytes
```

成功code=0、errorPosition=-1。consumed只累计自上次reset起成功提交帧的编码字节数。当前feed中已完成的帧即使随后出错也保留在该命令观察中；失败帧及当前块中后续已缓冲字节保留为残留。错误后被忽略的feed不推进consumed。reset命令自身观察为空成功状态。

V0线性序列/数组追加并搬移剩余字节；V1环形存储，通过head/count和mod32定位；V2复用环形版，但把无错误状态下的空feed当成丢弃残留。见证为feed`[1]`、空feed、finish：参考保留残留并报告截断，V2已经丢失数据。第2条命令的残留观察也可直接区分，因此不声称该负例发现很难。

32字节arena容量来自具体边界：成功排空后未完成帧至多10字节，一次feed至多8字节；错误后不再追加。该讨论不是安全证明，CompCert目标仍要求建立所有执行的安全和终止。调用链由`main→feed_chunk→drain_frames→checksum_frame→peek_byte`体现。

## S-TX 嵌套事务键值存储

输入`[q] ++ q条[op,key,value]`，0≤q≤64。op=0 set、1 erase、2 get、3 begin、4 commit、5 rollback。set/get/erase的key为0–7；set的value为±1000，get/erase的value为0；控制操作key/value均0。初始八键全空，事务深度为0。

set和erase修改当前映射；get观察当前映射。begin深度<8时新建savepoint，深度=8时报状态2且不修改状态。commit/rollback没有活动事务时报状态1且不修改状态；其他成功状态0。内层commit取消内层savepoint，但其修改仍受外层rollback管辖。rollback恢复最近savepoint并弹出它。允许事务未关闭时结束输入，不隐式commit或rollback。

每条命令观察`[op,status,found,value,depth]`；只有get的found/value有查询含义，其他命令写0/0。不存在的键为0/0。结束后追加`[depth] ++ 按key递增的八条[found,value]`，不观察快照、日志、mark或物理存储。

V0保存整张映射的快照栈；V1每次活动事务内写操作追加旧槽值，以mark标记savepoint，rollback按逆序恢复。内层commit保留日志，最外层commit清空日志。V2错误地在每次commit时截掉当前savepoint之后的日志。见证：begin、begin、set(0,7)、commit、rollback、get(0)。V0/V1回到空映射，V2保留内层写入。

最多64条操作意味着日志条目最多64，含重复写和删除不存在的键；错误和重复操作不由前提排除。核心调用链包括`execute_tx→tx_write→append_undo→read_slot`以及`execute_tx→tx_rollback→undo_to→restore_undo→write_slot`。同一键重复覆盖、内层回滚、内层提交后外层回滚和深度上限均需要关系不变式。

## S-LRU 带缩容与节点复用的缓存

输入`[initialCapacity,q] ++ q条[op,key,value]`，容量0–8，q为0–64。op=0 put、1 get、2 peek、3 erase、4 resize。普通key为0–15，resize把key字段解释为新容量0–8。put的value为±1000，其他value为0。初始空缓存，所有命中/未命中及容量变化都合法。

put已有键时更新值并移到MRU；新键在容量0时不保存，否则必要时先淘汰LRU再插到MRU。get命中移动到MRU，peek命中保持顺序；未命中不改变状态。erase命中删除，未命中不改变状态。resize改变容量，并按LRU到MRU顺序淘汰直到满足新容量。

每条命令观察`[op,status,value,evictionCount] ++ 被淘汰的[key,value]`。put状态1表示保存、0表示零容量未保存，观察value固定0；get/peek/erase状态为found，value为命中/被删的值，未命中为0；resize状态1、value为新容量。结束后追加`[capacity,size] ++ MRU到LRU顺序的[key,value]`。节点ID、空闲槽、prev/next与地址均隐藏。

V0用MRU顺序表，C中通过数组搬移；V1用8个结构体节点组成索引双向链表，查找扫描live槽，删除/淘汰后复用空闲槽。V2仅把get命中的touch遗漏；put更新仍移动到MRU。容量2时put(0,1)、put(1,2)、get(0)、put(2,3)、get(1)可区分淘汰与后续查询。因为最终MRU顺序也被观察，短于该轨迹的反例同样可能有效。

调用链`main→execute_cache→cache_put→evict_tail→erase_at→detach`要求连接顺序表与节点集合、前后链接、head/tail、容量和可复用槽。不得要求两种内部表示或整个最终内存相等。C的有限arena不掩盖真实内存更新语义；原生移植一致性目前仅由差分测试审查。

## 六个三平台待证明命题

| 任务ID | family/domain索引 | 固定实现对 | 暂定分支 |
|---|---|---|---|
| S-FRAME-RING | 0 | frames V0/V1 | 全域等价 |
| S-FRAME-EMPTY | 0 | frames V0/V2 | 具体反例 |
| S-TX-JOURNAL | 1 | transactions V0/V1 | 全域等价 |
| S-TX-COMMIT | 1 | transactions V0/V2 | 具体反例 |
| S-LRU-LINKS | 2 | lru V0/V1 | 全域等价 |
| S-LRU-TOUCH | 2 | lru V0/V2 | 具体反例 |

将ID中的`-`换成`_`并加`_equivalence`或`_refutationAt`，就是具体目标名。Lean定义在`lean/StatefulGoals.lean`，Rocq在`rocq/StatefulGoals.v`，C/CompCert在`compcert/FRAMESGoals.v`、`TRANSACTIONSGoals.v`和`LRUGoals.v`。规范接受目标另由三平台`StatefulTargets`模块绑定。

例如，Lean待证明定理为：

```lean
theorem solve : SpecLessBenchStateful.S_TX_JOURNAL_equivalence := by
  -- pending final proof
```

展开为`∀ x, valid 1 x → ∃ o, entry 1 0 x = some o ∧ entry 1 1 x = some o`。反例必须提交具体x/oa/ob并证明`valid d x ∧ entry f 0 x = some oa ∧ entry f j x = some ob ∧ oa ≠ ob`。Rocq命题同形；CompCert以固定编码注入标准初始化global，证明两程序安全有限终止且观察一致或不同。所有实现、域、观察与callee均受保护，允许模型自己推导辅助关系和函数契约，不提供第三份独立功能规约。
