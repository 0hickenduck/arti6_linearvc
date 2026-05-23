# Trellis 架构与工作流概览

> **核心哲学**：“Harness engineering is more about principle.” (框架工程更关乎原则)
> 
> Trellis 并不是一个臃肿且死板的巨型执行器，而是一个**轻量级的“状态机与上下文管理器”**。大模型（如 Gemini、Codex）具有极强的动态适应能力，如果框架过重，反而会限制模型的发挥。因此，Trellis 的设计理念是提供**最小化但严格的原则（Principle）**：维持项目状态、约束架构边界、规范文件产出；而具体的代码生成、工具调用和思路拓展，则完全交由 Agent 在上下文中动态发挥。

---

## 1. 整体架构：你的代码在哪里？

在当前的 ARTI-6 + LinearVC 实验中，项目被划分为以下几个清晰的层级，确保“思考”、“实验”与“核心代码”互不干扰：

- **`.trellis/`（大脑与中枢）**：
  - `spec/`：存放全局的技术规范、实验安全限制（如：不跑重度 GPU 任务）、系统架构原则。**这是唯一的 Truth (真理源)。**
  - `tasks/`：存放所有的“任务车间”。每个需求（如“搭脚手架”、“评估数据”）都在这里拥有独立的子文件夹。任务完成前，所有的草稿和研究都在这里进行。
  - `workflow.md`：全局状态机，驱动 Agent 遵循“计划 -> 执行 -> 验证”的循环。
- **`arti6_linearvc_demo/`（主干业务代码区）**：
  - 真正的高净值业务代码。AI 在 `.trellis/tasks/` 下完成脚手架和测试后，最终将可运行的代码迁移至此处。
- **`external/`（外部冻结依赖）**：
  - `arti-6/` 等克隆下来的第三方库。Agent 知道这些是只读的参照物，不能随意篡改。
- **`archive/`（历史区）**：
  - 存放旧的 `research_notes` 或废弃的实验文件，保持根目录整洁。

---

## 2. Agent 是如何协同工作的？

Trellis 采用的是**“大脑共享 + 专职打工”**的协作模式：

### (A) 前端无关 (Frontend Agnostic)
你可以今天用 Gemini CLI，明天用 Codex CLI。它们只是“交互前端”。
在根目录下，`.gemini/` 和 `.codex/` 只是各自工具的配置入口，它们都会指向共用的 `.trellis/scripts/hooks/` 和统一的 `.agents/skills/` 技能库。**这意味着所有 Agent 共享同一个项目记忆。**

### (B) 主从代理模式 (Sub-agent Delegation)
为了防止主会话的上下文（Context Window）爆炸，Trellis 将任务切分：
1. **主 Agent（我）**：负责跟你聊天、讨论需求（Brainstorm）、分配任务。
2. **`trellis-implement`（代码民工）**：一旦需求确定，主 Agent 会在后台唤醒它，它只负责读规范并写代码。
3. **`trellis-check`（质检员）**：写完代码后唤醒它，专门负责 Lint、Type-check 和规范核对。
4. **`trellis-research`（研究员）**：当你需要调研大量外部文档时，它会在后台默默检索并把结果写成 `.md` 报告。

---

## 3. 核心“技能”库 (Skills)

系统内置了约 10 个动态技能（存放在 `.agents/skills/` 下）。这些技能本质上是动态组装的 Prompt，当触发特定场景时，Agent 才会按需读取：

1. **`trellis-start`**: 会话启动时，初始化开发者身份和工作流状态。
2. **`trellis-brainstorm`**: 需求模糊时，引导 Agent 每次只问一个高质量问题，并生成标准的 `prd.md`。
3. **`trellis-before-dev`**: 编码前，强制 Agent 注入当前目录的特定开发规范（Spec）。
4. **`trellis-check`**: 代码写完后，进行质量验证。
5. **`trellis-break-loop`**: 如果某个 Bug 修复了 3 次还没修好，强制跳出死循环，进行深度复盘。
6. **`trellis-update-spec`**: 任务结束后，如果有踩坑经验，自动更新到 `.trellis/spec/` 中。
7. **`trellis-finish-work`**: 最终提交和收尾。
8. *(其他包括: `trellis-continue`, `trellis-meta`, `skill-creator` 等，用于恢复状态和扩展技能).*

---

## 4. 总结：它是否适合你的口味？

Trellis 的设计非常契合你所说的 **“Harness engineering is more about principle”**：
它 **没有** 复杂的 Python 后端去强行接管你的终端，**没有** 写死的文件生成路径，而是通过 Markdown 格式的**原则（Specs）**和**工作流指南（Workflow）**对大模型进行“软约束”。大模型依然可以根据实际情况动态规划工具（比如自己生成脚本来扫描文件，自己写正则提取日志），Trellis 只保证这些动态行为最终收束到正确的地方，不会把你的项目搞成一团乱麻。