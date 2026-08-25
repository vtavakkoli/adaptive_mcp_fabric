"""Adaptive MCP Fabric: progressive discovery and trust-aware MCP orchestration."""

from .benchmark import BenchmarkCase, BenchmarkResult, build_router_for_catalog, evaluate, synthetic_catalog
from .client import MCPHttpClient, MCPProtocolError
from .discovery import ProgressiveDiscovery
from .executor import ExecutionDenied, FabricExecutor
from .fabric import AdaptiveMCPFabric
from .models import ExecutionContext, ExecutionPlan, ExecutionReport, PlanStep, PolicyAction, PolicyDecision, RankedTool, RiskLevel, RouteDecision, ToolCapability, ToolResult, ToolStats
from .planner import DAGPlanner, PlanValidationError
from .policy import PolicyEngine, PolicyRule
from .registry import ToolRegistry
from .router import AdaptiveRouter, RouterWeights
from .scoring import SemanticScorer, TokenCosineScorer
from .telemetry import TelemetryStore

__version__ = "0.1.0"

__all__ = ["AdaptiveMCPFabric", "AdaptiveRouter", "BenchmarkCase", "BenchmarkResult", "build_router_for_catalog", "DAGPlanner", "ExecutionContext", "ExecutionDenied", "ExecutionPlan", "ExecutionReport", "FabricExecutor", "MCPHttpClient", "MCPProtocolError", "PlanStep", "PlanValidationError", "PolicyAction", "PolicyDecision", "PolicyEngine", "PolicyRule", "ProgressiveDiscovery", "RankedTool", "RiskLevel", "RouteDecision", "RouterWeights", "SemanticScorer", "TelemetryStore", "TokenCosineScorer", "ToolCapability", "ToolRegistry", "ToolResult", "ToolStats", "evaluate", "synthetic_catalog"]
