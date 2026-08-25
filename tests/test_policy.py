from adaptive_mcp_fabric import ExecutionContext, PolicyAction, PolicyEngine, RiskLevel, ToolCapability


def tool(**kwargs):
    return ToolCapability(server_id="demo", name="x", description="x", **kwargs)


def test_read_only_is_allowed():
    assert PolicyEngine().evaluate(tool(), ExecutionContext()).action is PolicyAction.ALLOW


def test_side_effect_requires_confirmation():
    assert PolicyEngine().evaluate(tool(read_only=False), ExecutionContext()).action is PolicyAction.CONFIRM


def test_critical_is_denied():
    assert PolicyEngine().evaluate(tool(risk=RiskLevel.CRITICAL, read_only=False), ExecutionContext()).action is PolicyAction.DENY


def test_custom_scope_rule():
    policy = PolicyEngine([PolicyEngine.require_scope("repo:write")])
    decision = policy.evaluate(tool(), ExecutionContext(scopes=frozenset({"repo:read"})))
    assert decision.action is PolicyAction.DENY
