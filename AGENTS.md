# 仓库指南

## WHAT：项目概览

本项目是一个面向本地权重模型的对齐训练仓库，当前重点是：

- 使用 `reward_seed.json` 这类偏好数据做 DPO 训练
- 针对本地模型目录（当前为 `/root/autodl-tmp/Qwen3.5-4B`）执行 LoRA / QLoRA 微调
- 在 AutoDL 环境中稳定跑通 Qwen3.5 相关依赖，包括 `fla`、`causal-conv1d`、CUDA toolkit
- 为训练过程提供统一日志和 WandB 监控接入

当前代码规模很小，主逻辑集中在：

- `scripts/`：训练脚本入口
- `core/`：日志等基础设施
- `.codex/rules/`：项目规范

## WHY：设计目标

- 让单机训练入口清晰、可复现、易排障
- 把环境稳定性约束沉淀到仓库，而不是留在临时对话里
- 统一日志、训练监控、输出目录约定，方便后续扩展更多训练脚本
- 保持脚本层和基础设施层分离，避免随着训练需求增加变成单文件堆叠

## 环境约束

- 默认语言：始终使用简体中文回复用户
- 当前主要运行环境：
  - Ubuntu 22.04
  - AutoDL 单机 GPU
  - Python 虚拟环境：`/root/venv/refuse/bin/python`
- 当前已验证的 Qwen3.5 训练运行时约束：
  - CUDA toolkit 13.0
  - `FLA_TILELANG=0`
  - `TRITON_F32_DEFAULT=ieee`

## 核心目录

- `scripts/`：训练脚本 CLI 入口
- `core/`：日志、训练基础设施
- `.codex/rules/`：Codex 项目规则
- `reward_seed.json`：偏好训练数据
- `DPO_LORA.md`：训练说明

## 核心命令

```bash
/root/venv/refuse/bin/python -m pip install --no-cache-dir -r requirements-refuse.txt

TMPDIR=/root/autodl-tmp/tmp \
CUDA_HOME=/usr/local/cuda-13.0 \
PATH=/usr/local/cuda-13.0/bin:$PATH \
LD_LIBRARY_PATH=/usr/local/cuda-13.0/lib64:$LD_LIBRARY_PATH \
CUDA_VISIBLE_DEVICES=0 \
/root/venv/refuse/bin/python scripts/train_dpo_lora.py \
  --model-path /root/autodl-tmp/Qwen3.5-4B \
  --data-path reward_seed.json \
  --output-dir /root/autodl-tmp/UniAlign-dpo-safe-lora
```

## Boundaries

### Always Do

- 改代码前先读相关文件，不要凭印象改结构
- 优先保持训练脚本入口清晰，复杂能力下沉到 `core/` 或后续新增模块
- 新增运行日志时统一使用 `core.logging`
- 训练相关输出默认写到数据盘，例如 `/root/autodl-tmp/...`
- 新增训练依赖或环境变量时，补到文档和脚本默认值里
- 修改训练链路后至少给出一条可验证证据：命令、日志、输出目录或烟测结果

### Ask First

- 新增大型第三方依赖，尤其是会重装 `torch`、`triton`、CUDA 相关依赖
- 修改训练目标、偏好字段语义、数据格式约定
- 删除或重命名现有脚本入口、输出目录结构
- 引入新的外部监控服务、实验管理服务或在线依赖

### Never Do

- 不要在库代码里散落 `print` 作为运行日志
- 不要新增根目录同名标准库文件，例如再次创建 `logging.py`
- 不要把临时构建缓存、checkpoint、测试输出直接扔进源码目录
- 不要默认把训练输出写进系统盘
- 不要未验证就批量升级 `torch / triton / fla / bitsandbytes`

## Progressive Disclosure

| 任务 | 首选参考 |
| --- | --- |
| 跑 DPO LoRA 训练 | `scripts/train_dpo_lora.py`, `DPO_LORA.md` |
| 统一日志接入 | `core/logging.py`, `.codex/rules/code_style.md` |
| 接入 WandB | 训练脚本、`.codex/rules/code_style.md` |
| 排查 Qwen3.5 训练稳定性 | `scripts/train_dpo_lora.py`, 环境变量约定, 相关 smoke test |

## 日志规则

- 新代码禁止直接使用 `print` 做过程日志
- 统一使用 `core.logging`
- 推荐使用方式：
  - `LOGGER = get_logger("DPOTrain")`
  - `LOGGER = init_script_logger("TrainDpoLora")`
  - `LOGGER = init_training_logger("qwen35_dpo_lora")`
- Logger 名必须是业务语义清晰的 PascalCase

## Rules

- `pre_commit_rule.md`：提交前规则
- `code_style.md`：代码风格、日志与 WandB 规范

上述规则以 `.codex/rules/` 为主维护目录。
