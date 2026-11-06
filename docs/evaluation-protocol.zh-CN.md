# SpecLessBench 评测指令审阅稿

状态：草稿，尚未用于运行。评测与监控保持暂停。

这是 SpecLessBench 独立的评测协议。下文将任务 prompt、平台接口和可选执行 skill 分开，供审阅。

## 任务 prompt

你需要判断给定的两个固定实现是否具有相同的可观察行为，并提交机器可检查的证明。任务文件位于只读目录 `/task`，你的工作目录是 `/work`。

任务文件定义输入域、观察结果和目标定理。请选择一个结论：

- 等价：证明两个实现对所有合法输入产生任务规定的相同行为。
- 不等价：给出一个具体合法输入，证明两个实现的观察结果不同。

将选择写入 `/work/claim.json`：

```json
{"claim":"equivalence"}
```

或：

```json
{"claim":"counterexample","input":[...],"left":[...],"right":[...]}
```

反例字段必须是字面整数列表，并遵守下方的平台接口。将证明写入指定的 Submission 文件，提供名为 `solve`、类型与所选目标一致的完整定理。你可以增加辅助定义和引理，证明方法不限。

实现、合法输入条件、观察语义和目标定理不可修改。证明不能包含未证明的占位符或自行引入的公理。测试可以帮助寻找反例，但提交的结论必须有形式化证明。

评分器独立检查提交文件、目标类型和公理依赖；全部通过才判为成功。

运行配置：总时间预算 `{budget_seconds}` 秒，最多 `{max_rounds}` 轮。时间由控制器统一计量，包括 agent 工作与评分检查；续跑沿用同一会话和工作目录。

## 平台接口（每次只发送当前平台）

### Lean

- 读取 `/task/Task.lean`。
- 提交 `/work/Submission.lean`，导入 `Task`，定义 `Submission.solve`。
- 等价目标为 `Task.equivalent`；反例目标为 `Task.refutationAt <input> <left> <right>`。
- 反例的 left/right 是 `some` 中完整的 Words，包含开头的载荷长度。
- 本地编译：`LEAN_PATH=/task:/work lean /work/Submission.lean`。
- 不允许 `sorry` 和候选程序自行引入的公理；评分器允许 Lean 标准的 `propext`、`Classical.choice`、`Quot.sound`。

### Rocq

- 读取 `/task/Task.v`。
- 提交 `/work/Submission.v`，导入 `From Trusted Require Import Task.`，定义顶层定理 `solve`，不要再包裹 `Module Submission`。
- 等价目标为 `Task.equivalent`；反例目标为 `Task.refutationAt <input> <left> <right>`。
- 反例的 left/right 是 `Some` 中完整的 Words，包含开头的载荷长度。
- 本地编译：`coqc -Q /task Trusted -Q /work Candidate /work/Submission.v`。
- 不允许 `Admitted`、`admit` 或候选程序自行引入的公理；最终证明还须通过独立的 `coqchk` 检查与公理审计。

### CompCert / Clight

- C 源码为 `/task/Left.c`、`Right.c`；权威 Clight AST 为 `Left.v`、`Right.v`。`Task.v` 和 `Execution.v` 定义目标与执行语义。
- 提交 `/work/Submission.v`，导入 `From Trusted Require Import Task Execution Left Right.`，定义顶层定理 `solve`。
- 等价目标为 `Task.equivalent`，包含任务规定的安全性、终止性及观察结果要求。
- 反例 claim 的 input 是未填充的输入；left/right 包含长度槽和有效载荷。评分器分别补零至 8192 个字，并与主函数返回值 0 配对。相应定理为：

```coq
Task.refutationAt input
  (0%Z, left ++ repeat 0%Z (8192 - left_length))
  (0%Z, right ++ repeat 0%Z (8192 - right_length))
```

- 使用字面列表及其实际长度。完整输出缓冲区是现有任务语义的一部分。
- 可以使用函数模型，但必须证明它与原有 Clight 执行语义的对应关系。
- 本地编译：`coqc -Q /task Trusted -Q /work Candidate /work/Submission.v`。
- 不允许 `Admitted`、`admit` 或候选程序自行引入的公理；允许评分器白名单中的 CompCert 标准假设，仍需独立检查及公理审计。

## 可选执行 skill：检查并完成证明

本节用于“强化验收”条件；基础条件不提供本节。不要同时把相同要求再追加到任务 prompt。

围绕所选目标编写证明，并使用平台给出的命令检查最终提交文件。检查失败时，根据错误修改证明或调整证明方法，再次检查；没有完成证明不是结束工作的理由。继续工作直到提交文件检查通过，或控制器终止本次运行。

提交前确认：claim 与证明分支一致，`solve` 是完整的指定目标，最终文件编译成功。若评分器随后返回拒绝，在原会话中根据检查日志继续处理。无法解决的错误应如实保留，不得使用占位符、额外假设或更改目标取得通过。

本地编译成功后可以交回提交物供控制器评分；只有独立评分器通过才算成功。agent 无须等待一个未暴露给它的评分工具，也不应声称已经调用该工具。

## 续跑消息

所有条件使用同一份结构化检查反馈，避免把额外提示混入对照：

```text
本轮评分结果：{result}
剩余共享时间：{remaining_seconds} 秒
剩余轮数：{remaining_rounds}
检查日志：
{checker_output}
```

控制器负责是否启动下一轮。反馈不透露预期分支、其他题目或参考证明。

## 对照与记录

历史验证产物已按用户要求删除，评测从零开始。保留原版与强化版提示模板用于后续对照，不复用历史通过结果。

若采用本草稿做新的对照，两组使用相同任务 prompt、平台接口、模型、预算、轮数和评分器；仅改变是否提供执行 skill。这样比较的是明确的“验收执行指导”因素。

每个 attempt 记录实际发送的 prompt、平台接口、skill（没有则为空）、各自版本与 SHA-256、续跑策略及每轮真实消息。分析时按这些字段分组，不能只根据通过与否或运行日期推断提示版本。所有版本信息在新运行启动时记录，不事后推断。

历史原版已有本地编译命令，不应把它描述为“完全没有检查要求”。当前沙箱尚未提供 agent 可调用的独立评分脚本；若后续增加，应保证两组具有相同工具访问权限，并单独记录工具版本。
