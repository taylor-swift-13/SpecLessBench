# SpecLessBench pilot v1：冻结与发布状态

这是一份 **71 个语义上下文、30 个切分家族、213 个平台实例**的冻结源码快照。它还不是可交付求解器的正式评测包。`manifest.json` 只含无语义的 pilot ID、匿名家族 ID、平台和快照信息；不含整理端原题号、预期极性或反例输入。

## 快照和复现

冻结时记录了 472 个受保护任务／目标文件的哈希，另以独立 addendum 绑定输入校验器、构建配置、注册表、构建脚本和编译器可执行文件。原始源码和构建支持共 591 个文件的快照位于 WSL 私有目录中的 `frozen-sources.tar.gz`，受 `manifest.json` 的哈希约束。工具可执行文件有哈希，但完整标准库、系统和内核尚未锁定。

私有材料位于 WSL 的 `~/.local/share/speclessbench/pilot-v1/`，目录权限为 `0700`，文件权限为 `0600`；其中包含原题映射、随机 secret、冻结源码和可能暴露标签的日志。Windows 挂载目录上的 `chmod` 不能作为 Unix 私有权限保证，因此不把映射留在仓库目录。**必须由整理方自行安全备份该 WSL 目录**；不要将它挂载到求解器，也不要把它推送到公开仓库。丢失 secret 或映射后，不能从匿名 ID 恢复已冻结的对应关系。

在 WSL 的既有工具链环境中执行：

```bash
python3 scripts/pilot/verify_freeze.py
python3 scripts/pilot/verify_archive.py
python3 scripts/pilot/verify_audit.py
```

第一项检查当前工作区的冻结任务文件；日后如工作区继续修改而触发失败，应使用备份的冻结源码与新工作区，不要修改 pilot 来追随工作区。其余检查验证私有归档和审计证据。

## 三平台检查

在不改动冻结源的独立副本中，已重新执行三平台构建；103 个重新导出的 Clight AST 与冻结版本逐字节一致。71 个上下文的正反分支接口在 Lean、Rocq 和 CompCert 工具链中重新通过类型检查。结果见 `platform-audit.json`、`ast-audit.json` 和 `interface-audit.json`，具体构建日志放在 WSL 私有目录的 `audit-logs/`。

另外针对全部 213 个平台实例，生成并检查了 213 个等价目标类型和 213 个带字面量输入的反例目标类型；见 `obligation-audit.json`。反例目标检查使用任意合法探针输入和人为构造的不同观察值，它们不代表有效反例。24 份编译日志保存在私有的 `obligation-logs/`。

这些检查不是最终题目证明，也不证明三个平台版本相互精化；CompCert 的 Clight 语义仍未做逐任务执行或最终证明。

## 隔离与泄漏：尚未达到发布条件

`leak-audit.json` 记录了旧任务编号和共享源码中的显式提示风险。新索引本身不暴露原题号，但**中性编号不是完整的防泄漏求解包**：共享源码中还有 `mutant` 等提示、其他版本的分支和原符号；原仓库公开历史也已存在。真正发布前必须逐题裁剪和匿名化模型可见内容、验证其绑定到原目标，并独立复核泄漏。

`scripts/pilot/sandbox.py` 是评分边界原型：使用 bubblewrap 的文件系统／网络／进程命名空间和用户级 systemd cgroup，设置资源上限，并记录作业级内存峰值。`grader-prototype.json` 仅记录玩具命题测试：正常证明、`sorry`／`Admitted`、额外公理、错误目标及文件／网络／资源限制等。它尚未接入真实题目的可信封装；Rocq 假设检查输出、加载器和对抗场景仍需审计，且共享主机内核并非完整虚拟机安全边界。

简化执行链由 `scripts/pilot/single_task_runner.py` 和 `scripts/pilot/grade_sealed.py` 提供。前者将整理方提供的单题目录按可信哈希复制后只读挂入沙箱，每次新建工作目录；后者重新核验独立的可信目标包，调用相应平台的证明检查器。Lean 允许 `propext`、`Classical.choice`、`Quot.sound`，拒绝其他证明依赖；Rocq/CompCert 目前保守地拒绝所有公理。题目目录、哈希和待评分目标必须由可信的整理方选择，不能由 agent 指定。两个目录可以不同：agent 可见目录只能放该题所需材料，可信评分目录可以包含 agent 不可见的检查依赖。

`test_single_task_runner.py` 检查其他目录、前次运行及题目篡改隔离；`test_grade_sealed.py` 对三个工具链测试接受合法证明和拒绝未完成证明、额外公理、篡改目标包；`test_attempt_to_grade.py` 测试从沙箱输出到 Lean 评分的完整链路。这些测试使用玩具命题。

第一道真实 Lean 等价题已接入：`python3 scripts/pilot/prepare_factorial.py` 从冻结实现建立单题包，并用 Lean 检查裁剪后正反目标与原目标的对应关系；这不是最终任务证明。`python3 scripts/pilot/test_real_factorial.py` 对真实目标检查了 `sorry`、额外公理及错误目标均被拒绝。评分入口为 `python3 scripts/pilot/release_gate.py --task P-dbec465c356ed73d --platform lean --proof /path/to/Submission.lean`；提交需定义 `Submission.solve : Obligation.goal`。在沙箱中只挂载 `_build/pilot-v1/first-real-task/task/`，不要挂载其父目录、仓库或评分器目录。**目前只支持这一道题的 Lean 等价分支**，其反例分支及其余题目、平台还未接入；文件哈希本身不能证明目录没有其他题或目标绑定正确。

2026-11-05 的原型测试继续向 `benchmarks/construction/pilot-jobs.jsonl` 记录沙箱作业的 cgroup 资源；本次外层命令没有逐条加入早期的命令计时器，因此总命令时间仍不完整。`pilot-freeze-v0.12` 的 token 快照覆盖了两次用户请求，时间窗口包括两次请求之间的等待，不能当作实际工作时长。

因此 `scripts/pilot/release_gate.py` 对其余未封装题目返回 `unavailable`，不会给出成功分数。构造和审计成本在 `benchmarks/construction/` 单独保留，不虚报为完整历史成本。
