"""Core infrastructure for UniAlign."""

from .logging import (
    DEFAULT_LEVEL,
    LOGGER_COLORS_EXACT,
    LOGGER_PATTERNS,
    get_logger,
    init_component_logger,
    init_script_logger,
    init_training_logger,
    register_logger_color,
    register_logger_pattern,
    setup_file_logging,
)

from .training import (
    CheckpointLoggingCallback,
    build_model,
    configure_wandb,
    create_tokenizer,
    get_world_size,
    load_config,
    load_model_with_adapter,
    log_cuda_memory,
    log_effective_batch,
    set_runtime_env,
)

__all__ = [
    "DEFAULT_LEVEL",
    "LOGGER_COLORS_EXACT",
    "LOGGER_PATTERNS",
    "get_logger",
    "init_component_logger",
    "init_script_logger",
    "init_training_logger",
    "register_logger_color",
    "register_logger_pattern",
    "setup_file_logging",
    "build_model",
    "CheckpointLoggingCallback",
    "configure_wandb",
    "create_tokenizer",
    "get_world_size",
    "load_config",
    "load_model_with_adapter",
    "log_cuda_memory",
    "log_effective_batch",
    "set_runtime_env",
]
