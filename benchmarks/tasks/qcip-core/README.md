# QCIP 派生的四家族具体任务（design-v0.1）

**v0.2 更新优先于下方 v0.1 历史说明。** 每个任务现要求 Lean、原生 Rocq、C/CompCert 三版，四组12个语义上下文对应36个平台实例；见 [THREE-PLATFORM.md](THREE-PLATFORM.md) 和 [three-platform.json](three-platform.json)。构造阶段不要求最终命题的证明，允许带日志的实现修订与任务修改；冻结后的求解阶段仍禁止修改实现。Lean/原生Rocq定义及目标类型已经检查，Clight导出仍待完成。完整过程和成本记录见 [construction/PROTOCOL.md](../../construction/PROTOCOL.md)。

这里将 BST、AVL、环形缓冲区、Dijkstra 落实为 **16 个固定 C 入口、12 个待证明任务**。每个家族有 `V0/V1/V2` 三个候选等价实现和一个 `V3` 变异实现，选择 `V0/V1`、`V0/V2`、`V0/V3`，不把所有两两组合充当独立样本。它们细化既有的 12 个目录槽位，不增加全库的 22 条目／54 槽位计数。

**当前状态：source-concrete，尚未 reference-ready。** C 入口、所有源级 callee、输入编码、观察输出和待证明命题已写出；有限 native 构建检查已运行。没有尝试新证明。CompCert 3.16 的 Clight AST 生成、接口类型检查、依赖锁定和参考证书仍待完成，不能据此声称任何一题已被形式化证明或反驳。`rocq/*Bindings.v` 直接引用将来导出的具体 AST 模块，缺失时会构建失败，不用公理或参数冒充实现。

## 文件入口

- [TASKS.md](TASKS.md)：逐家族的域、编码、观察、三道题和定理。
- [tasks.json](tasks.json)：实现／目标绑定、划分组和受保护文件哈希。
- [rocq/Domain.v](rocq/Domain.v)：四个输入类型、有效域和序列化定义。
- [rocq/Execution.v](rocq/Execution.v)：输入注入、Clight 安全执行、输出投影和 Eq/Cex 定义。
- `rocq/*Expected.v`：12 个整理端预期分支定理声明。
- `rocq/*Certificates.v`：12 个公开析取目标声明。
- [curator-witnesses.json](curator-witnesses.json)：四个候选反例及预期差异，只供整理端。
- [PROVENANCE.md](PROVENANCE.md)、[NOTICE.md](NOTICE.md)：来源、显式改动和许可证。
- [evidence/native-check.json](evidence/native-check.json)：本轮有限执行记录，**不是形式化证书**。

`Theorem ... Abort.` 表示该命题明确留待证明；`Abort` 不导出定理常量，也不引入公理。当前目标声明未用 CompCert 类型检查。将来求解者提供独立证明文件并证明相同的受保护 `Certificate` 命题，不能把 `Abort` 文件编译成功算作完成。

## v0.1历史构建与检查（当前v0.2请用THREE-PLATFORM.md命令）

```sh
python3 scripts/curation/check_qcip_core.py
python3 scripts/curation/check_qcip_core.py --native
# 仅在已安装并锁定 CompCert 3.16 / x86_64-linux 后导出 AST，不运行任务证明：
python3 scripts/curation/check_qcip_core.py --export-clight
```

前两个命令均不运行 `coqc` 或 `coqchk`。Native 检查将固定入口预处理为 `_build/qcip-core/c/*.c`，通过另外的 stdio harness 批量喂输入；harness 不属于 Clight 程序。使用 GCC 的 AddressSanitizer 和 UndefinedBehaviorSanitizer；随机种子为 `20261103`。有限测试只能发现任务构建错误，不能确认全称等价、全域安全或负例标签。

导出命令生成 `_build/qcip-core/ast/*.v` 及 AST/source 哈希记录。它不自动安装工具，不产生证明，不自动把导出结果升级为受保护资产。后续还须记录 `clightgen` 二进制哈希、完整目标架构/ABI、CompCert 与 Rocq 的可复现依赖版本，再对导出 AST 做闭包检查并冻结。逻辑路径规划为：

```text
-Q benchmarks/tasks/qcip-core/rocq SpecLessBench.QCIP
-Q _build/qcip-core/ast SpecLessBench.QCIP.Generated
```

`prepare_qcip_core.py --refresh` 是**有意修订题目**时才运行的整理命令：它重生成绑定和目标、更新哈希；评测过程不得调用它。

## 发布边界

本目录整体属于整理端资产，尚无隔离后的 agent package。不能把本 README、`TASKS.md`、预期分支、变异说明、反例种子或全部四个实现一起交给模型。发布器应只提供选中两份程序、公共域/观察/语义接口、无极性泄漏的目标和证明工作区；将程序及文件名中性重命名，并重新冻结绑定。源系统的 annotation 和参考证明不进入任务包。

同一家族的所有实现、三个任务、输入域变体及未来相关移植保留在同一个 `split_group_id`。Dijkstra 的两个队列与 client 目前通过可见头文件合并成一个翻译单元，以便导出一个完整 AST；逻辑模块调用仍存在。这一版不能作为真实分离编译／跨翻译单元链接实验的完成品。
