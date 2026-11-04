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

因此 `scripts/pilot/release_gate.py` 对所有真实题目故意返回 `unavailable`，不会执行提交，更不会给出成功分数。只有逐题封装、证书绑定和隔离审计通过后，才应实现并启用正式评分入口。构造和审计成本在 `benchmarks/construction/` 单独保留，不虚报为完整历史成本。
