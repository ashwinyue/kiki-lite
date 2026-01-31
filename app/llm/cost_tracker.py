"""成本追踪模块（简化版）"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CostRecord:
    """成本记录"""
    model: str
    input_tokens: int
    output_tokens: int
    cost: float


@dataclass
class CostSummary:
    """成本汇总"""
    total_cost: float
    total_input_tokens: int
    total_output_tokens: int
    request_count: int


class CostTracker:
    """成本追踪器（简化版）"""

    def __init__(self, budget: Optional[float] = None) -> None:
        self.budget = budget
        self._records: list[CostRecord] = []

    def track(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """追踪一次 LLM 调用成本"""
        cost = (input_tokens * 0.00001 + output_tokens * 0.00003)
        self._records.append(CostRecord(model, input_tokens, output_tokens, cost))
        return cost

    def get_summary(self) -> CostSummary:
        """获取成本汇总"""
        total = sum(r.cost for r in self._records)
        return CostSummary(
            total_cost=total,
            total_input_tokens=sum(r.input_tokens for r in self._records),
            total_output_tokens=sum(r.output_tokens for r in self._records),
            request_count=len(self._records),
        )


# 全局成本追踪器
_cost_tracker: Optional[CostTracker] = None


def get_cost_tracker() -> CostTracker:
    """获取全局成本追踪器"""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker()
    return _cost_tracker


def set_cost_tracker(tracker: CostTracker) -> None:
    """设置全局成本追踪器"""
    global _cost_tracker
    _cost_tracker = tracker


def track_llm_call(model: str, input_tokens: int, output_tokens: int) -> float:
    """追踪 LLM 调用"""
    return get_cost_tracker().track(model, input_tokens, output_tokens)


def record_llm_usage(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cost: float,
) -> None:
    """记录 LLM 使用情况"""
    pass  # 简化实现


def get_cost_summary() -> CostSummary:
    """获取成本汇总"""
    return get_cost_tracker().get_summary()


def get_model_pricing(model: str) -> dict:
    """获取模型定价"""
    return {"input_price": 0.00001, "output_price": 0.00003}


def register_model_pricing(model: str, input_price: float, output_price: float) -> None:
    """注册模型定价"""
    pass


def check_budget(budget: float) -> bool:
    """检查预算"""
    return get_cost_summary().total_cost < budget
