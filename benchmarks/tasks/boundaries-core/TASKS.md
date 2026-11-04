# 输入观察与待证明目标

这里的行为说明解释固定实现及其比较范围，不是要求求解器另证的第三份功能规约。`BoundaryDomain`定义精确传输域，`BoundaryNative`和C程序定义行为，`BoundaryGoals`与各组CompCert目标直接引用这些实现。

所有输入是整数列表。C补零放入8192字输入global；程序返回0，清零输出global并写入长度和payload。原生观察是`Some (length :: payload)`，`None`是失败。C观察是返回值与初始化的完整输出global；任务不比较其他最终内存。下面均写payload，不重复长度前缀。

## TREE 指针树镜像

输入`[n] ++ n条[label,left,right]`。`0≤n≤64`，标签±1000，节点i的孩子只能为-1或`0≤child<i`，非空孩子在整个森林中最多出现一次；根为n-1，空树根为-1。可有不可达森林节点，它们不参与观察。C节点为预分配数组中的真实指针。

观察`[height] ++ preorder`：每个非空节点写`[id,label]`，空孩子写`[-1]`。这保留可见节点对应和形状，不能仅凭高度相等通过。V0递归交换并访问两个孩子；V1显式指针栈；V2只递归新左孩子。三节点左链能区分V0/V2，即使高度相同。

## UF 连通查询轨迹

输入`[n,q] ++ q条[op,a,b]`。`1≤n≤64`，`0≤q≤64`，op=0合并、1查询，`0≤a,b<n`；初始为单元素集合。按rank合并，rank相等时把a根挂到b根并增加b的rank。V0完整路径压缩，V1路径减半，V2的find只返回直接父亲。

每条合并观察`[0,0]`，查询观察`[1,connected]`；不观察代表ID或内部parent数组。见证：合并(0,1)、(2,3)、(1,3)，再查询(0,3)。V2不会依赖未定义行为形成反例。

## PQ 最大优先队列

输入mode=0时为`[0,q] ++ q条[op,value]`，`0≤q≤64`，op=0push、1pop、2peek、3empty，只有push允许非零value，范围±10⁶。空队列查询合法。每个push输出`[0,0]`；empty输出`[3,bool]`；pop/peek输出`[op,found,value]`，空时found/value均0。

mode=1为`[1,n] ++ n个值`，n≤64，先逐项push再全部pop，观察完整弹出序列。V0最大堆，V1降序数组，V2下沉忽略右孩子。正向上下文只取mode=0；反例上下文只取mode=1。`[9,7,8,1]`是区分见证。底向上建堆这一原候选替代尚未落实，不计入本批任务。

## EVAL 带错误的共享表达式图

输入`[n,e] ++ e个环境值 ++ n条[tag,a,b]`，`1≤n≤64`，e为0–8，环境值±1000。节点索引形成DAG，根为n-1，允许共享和不可达节点。

tag=0常量（a±1000,b=0），1变量（a为0–15,b=0，可未绑定），2加、3减、4小于、5相等、6AND、7OR、8负号、9NOT、10除法。已知非叶子引用更早节点，8/9的b=0；其他二元节点的a/b均有效。tag11–255是合法输入中的未知指令，a/b±1000但不解释。未知指令、未绑定变量、除零和语义溢出不从前提中排除。

观察`[code,errorNode,value]`。成功为`[0,-1,v]`；错误code为1未绑定、2结果超[-32768,32767]、3除零、4未知指令，value=0。除法向零截断。先处理左错误；AND左为0返回0，OR左非0返回1，均不传播被跳过右侧错误；其他运算处理右错误，再检查当前节点。V0按需递归并缓存；V1拓扑序DP可计算不可达/被跳过错误，但不让它们改变根观察；V2在短路前传播右错误。节点CONST0、未绑定VAR0、AND(0,1)即为区分见证。

## TLV 字节解析

输入`[n] ++ bytes`，0≤n≤96，字节0–255，**所有格式错误内容合法**。每条记录`[tag,lenLo,lenHi,payload...,checksum]`，长度小端，checksum为头和payload异或。tag1要求长度2并输出小端uint16；tag2允许0–32原始字节；tag3要求长度1且布尔值0/1。

观察`[code,offset,acceptedCount] ++ acceptedRecords`。成功offset=n。已接受tag1记录输出`[1,value]`，tag2输出`[2,len,bytes...]`，tag3输出`[3,value]`。失败只保留先前完整记录，不提交当前记录。

验证顺序固定：剩余不足3→code1；未知tag→2；长度>32→3；payload及checksum不足→4；typed长度不符→5；checksum错误→7；布尔值>1→6。code1–5的offset是记录开头，7是checksum位置，6是布尔payload位置。多错误输入按此顺序保留参考行为。V0索引循环，V1后缀递归；V2仅颠倒uint16字节序。`[1,2,0,1,2,0]`产生513与258。

## QUOTES 引号分词

输入`[n] ++ bytes`，0≤n≤64，字节0–255，空字节与不闭合引号均合法。只在引号外把TAB/空格当分隔符；单/双引号分别为39/34；单引号外反斜杠转义下一个字节，双引号内也适用；单引号内反斜杠为普通字节。相邻片段拼成一个词元，空引号产生空词元。这是私有分词规则，不是POSIX shell。

观察`[code,offset,tokenCount] ++ 每个[len,bytes...]`。成功offset=n。NUL错误code3且位置为当前字节，优先于转义处理。结尾悬空反斜杠code1，位置为反斜杠；优先于未闭合引号code2，后者位置为开引号。错误保留已完成词元，丢弃当前部分词元。V0逐字节状态机；V1在引号外一次吞普通字节跨度；V2开引号不置active标志，丢失空词元。`[34,34]`即可区分。

## PACK 重复与字面块解码

输入`[n,capacity] ++ bytes`，n为0–64，capacity为0–96，字节0–255，所有截断与超容量内容合法。控制字节0–127表示随后c+1个字面字节；128为空操作；129–255表示随后一个字节重复257-c次。

观察`[code,offset,producedCount] ++ decodedPrefix`。成功offset=n。每块先检查源长度（错误1），再检查输出容量（错误2），错误位置均为块头；失败块原子不提交，先前完成输出保留。V0索引循环，V1后缀递归，V2重复次数少1。capacity=4、字节`[255,65]`观察两个65与一个65。任务仅验证本有界接口，不主张外部格式标准的完整符合性。

## PATH 词法路径归一化

输入`[n] ++ bytes`，n为0–64，字节0–255。NUL合法并返回`[1,firstNUL,0]`。其他输入输出`[0,n,len] ++ result`。只做词法处理，不访问文件系统或解析符号链接。

斜杠47分隔组件，开头斜杠表示绝对路径，忽略空组件、`.`和末尾分隔符。`..`抵消先前普通组件；相对路径未匹配的`..`保留，绝对路径超根的`..`丢弃。空相对结果为`.`，空绝对结果为`/`，其他字节保留。V0左到右栈；V1右到左待抵消计数；V2错误抵消前一个`..`。`../..`区分`../..`与`.`。

## 16个具体待证明问题

每行给出同一输入域和观察下的固定实现对，两种分支都公开；预期极性只供整理端使用。

| 任务ID | 固定实现对 | 域索引 | 暂定分支 |
|---|---|---|---|
| C-TREE-STACK | TREE V0/V1 | 0 | 等价 |
| C-TREE-SUBTREE | TREE V0/V2 | 0 | 反例 |
| C-UF-HALVING | UF V0/V1 | 1 | 等价 |
| C-UF-ONEHOP | UF V0/V2 | 1 | 反例 |
| C-PQ-REP | PQ V0/V1 | 2 | 等价 |
| C-PQ-CHILD | PQ V0/V2 | 3 | 反例 |
| C-EVAL-DP | EVAL V0/V1 | 4 | 等价 |
| C-EVAL-SHORTCIRCUIT | EVAL V0/V2 | 4 | 反例 |
| B-TLV-CURSOR | TLV V0/V1 | 5 | 等价 |
| B-TLV-ENDIAN | TLV V0/V2 | 5 | 反例 |
| B-QUOTE-SPANS | QUOTES V0/V1 | 6 | 等价 |
| B-QUOTE-EMPTY | QUOTES V0/V2 | 6 | 反例 |
| B-PACK-SUFFIX | PACK V0/V1 | 7 | 等价 |
| B-PACK-REPEAT | PACK V0/V2 | 7 | 反例 |
| B-PATH-REVERSE | PATH V0/V1 | 8 | 等价 |
| B-PATH-PARENTS | PATH V0/V2 | 8 | 反例 |

将ID中`-`换为`_`后加`_equivalence`或`_refutationAt`，即为各平台的具体目标名称。例如Lean原生待证明命题为：

```lean
theorem solve : SpecLessBenchBoundary.C_EVAL_DP_equivalence := by
  -- pending
```

其定义展开为`∀ x, valid 4 x → ∃ o, entry 3 0 x = some o ∧ entry 3 1 x = some o`。反例分支需先提交具体x/oa/ob，再证明`valid d x ∧ entry f 0 x = some oa ∧ entry f j x = some ob ∧ oa ≠ ob`。Rocq原生命题同形；CompCert用`Execution.run`替换函数求值，要求标准boot输入、所有可达状态不stuck及无外部事件的有限终止，并比较固定输出投影。目标分别位于`lean/BoundaryGoals.lean`、`rocq/BoundaryGoals.v`与`compcert/*Goals.v`。

禁止只提交逻辑析取、超域输入、失败求值相等，或把测试见证称为形式化证书。所有最终命题在构造截断处保持未证明。
