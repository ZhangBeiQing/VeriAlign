# 代码风格与日志规范

本规则补充 `pre_commit_rule.md`，约束本仓库在本地模型对齐训练场景下的编码、日志和监控接入方式。

## 1. 基本代码风格

- Python 统一使用 4 个空格缩进。
- 变量、函数使用 `snake_case`。
- 类、具名组件、日志组件名使用 `CapWords` / PascalCase。
- 优先显式导入，禁止 `from x import *`。
- 训练入口放在 `scripts/`，公共基础设施放在 `core/`。
- 复杂行为补充类型注解和简短 docstring。

## 2. 设计偏好

- 优先组合而不是深继承。
- `scripts/` 只放 CLI、参数解析、主流程编排。
- 模型加载、日志、监控、数据转换等可复用逻辑优先下沉。
- 环境稳定性依赖必须收口在代码和文档中，不要只留在临时命令历史里。

## 3. 日志系统总则

本项目日志设计沿用现有 `logging.py` 的输出风格，但语义适配当前训练项目。

- 禁止在库代码里直接使用 `print` 做运行日志。
- 禁止新增裸 `logging.getLogger(__name__)` 或点路径风格 logger 名称。
- 必须优先使用 `core.logging` 提供的统一入口：
  - `get_logger(...)`
  - `init_component_logger(...)`
  - `init_script_logger(...)`
  - `init_training_logger(...)`

允许保留 `print` 的场景：

- CLI 最终结果输出
- demo / 手工调试入口
- 必须直接向终端展示的用户提示

## 4. Logger 命名规则

- Logger 名必须是**具业务含义的 PascalCase 组件名**。
- 推荐：
  - `DPOTrain`
  - `DPOData`
  - `DPOTrainer`
  - `ModelLoader`
  - `TokenizerSetup`
  - `WandbSetup`
  - `TrainingMetrics`
  - `Checkpointing`
- 允许的模块内写法：

```python
from core.logging import get_logger

LOGGER = get_logger("SelectionAnnouncements")
LOGGER.info("loaded %d records", count)
```

- 不推荐：
  - `__name__`
  - `scripts.train_dpo_lora`
  - `training.metrics.loop`

如果是带 rank / worker 标识的动态名字，使用：

- `[{Component} Rank {N}]`
- 例如：`[DPOTrain Rank 0]`

## 5. 日志级别约定

- `DEBUG`: 详细跟踪，只用于排障或低频路径。
- `INFO`: 阶段性里程碑、关键状态切换、输入输出摘要。
- `WARNING`: 可恢复问题、降级、跳过、兼容路径继续执行。
- `ERROR`: 当前步骤失败，需要人工关注。
- `CRITICAL`: 整个训练流程不可继续。

不要把正常流程刷成 `WARNING`，也不要把真正失败写成 `INFO`。

## 6. 输出与落盘规则

- 统一日志头为 `(UniAlign)`。
- 控制台日志使用按组件分类的颜色；`WARNING` / `ERROR` 颜色优先级高于组件颜色。
- 组件日志默认同时写：
  - 当前组件自己的时间戳日志文件
  - 同目录下的 `merged.log`
- 推荐目录约定：
  - 训练脚本：`logs/scripts/{ComponentName}/`
  - 训练 run：`logs/training/{run_name}/`
  - 通用组件：`logs/components/{ComponentName}/`

## 7. 新增组件如何接入日志

### 7.1 普通模块

```python
from core.logging import get_logger

LOGGER = get_logger("ModelLoader")
```

### 7.2 脚本 / 主入口

```python
from core.logging import init_script_logger

LOGGER = init_script_logger("TrainDpoLora")
```

### 7.3 训练 run

```python
from core.logging import init_training_logger

LOGGER = init_training_logger("qwen35_dpo_lora")
```

## 8. WandB 规范

- 统一通过 `transformers` / `trl` 的 `report_to="wandb"` 接入，不要同时手写重复上报逻辑。
- 需要额外记录训练前环境信息时，可单独写 `WandbSetup` logger，但不要把每一步 loss 再手动双写到 WandB。
- 默认假设用户已经执行过：

```bash
wandb login
```

- 在线模式优先；只有网络受限时才退到离线模式。
- 与 WandB 相关的可配置项应通过 CLI 参数或环境变量暴露，不要把账号信息写入代码。

## 9. 颜色注册规则

如果新增的是长期存在的核心组件，需要在 `core/logging.py` 里注册颜色：

- 优先更新 `LOGGER_COLORS_EXACT`
- 如需按前缀匹配，再更新 `LOGGER_PATTERNS`

不要在业务文件里自己写颜色逻辑。

## 10. 迁移原则

- 新改动必须使用 `core.logging`。
- 旧模块如果本次被修改，顺手迁移到 `core.logging`。
- 不要求一次性迁移所有历史代码，但新增训练链路和主路径必须遵守本规则。
