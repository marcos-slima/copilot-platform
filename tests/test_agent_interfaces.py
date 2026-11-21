"""Contrato de composição de interfaces pelo SDK."""

import json

from fastapi.testclient import TestClient

from app.config import settings
from app.models import DiagnosisResponse
from app.sdk import A2AConfig, AgentInterfaces, MCPConfig, MCPTool, ToolPolicy, asgi_app


def test_product_interfaces(monkeypatch):
    monkeypatch.setattr(settings, "api_key", "synthetic-mcp")
    monkeypatch.setattr(settings, "a2a_api_key", "synthetic-a2a")
    monkeypatch.setattr(settings, "a2a_base_url", "https://agent.example")
    monkeypatch.setattr(settings, "redis_url", "")
    calls = []

    def echo(value: int) -> int:
        calls.append(value)
        return value

    def diagnose(request):
        return DiagnosisResponse(
            probable_root_cause=request.description,
            model_confidence=0.0,
            diagnosis_confidence=0.0,
            next_steps=[],
            report_markdown="# Diagnóstico sintético",
        )

    def tool(name, scope):
        return MCPTool(
            name,
            echo,
            ToolPolicy(name, "low", False, (scope,), False, "public"),
        )

    card = {
        "name": "Agente sintético",
        "description": "Interface de teste",
        "version": "0.1.0",
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/markdown"],
        "skills": [{"id": "synthetic", "name": "Sintético", "description": "Teste", "tags": []}],
    }
    a2a = A2AConfig(card, diagnose, "synthetic")
    product = asgi_app(
        interfaces=AgentInterfaces(
            a2a=a2a,
            mcp=MCPConfig(
                "synthetic",
                "0.1.0",
                (tool("echo", "test.read"), tool("restricted", "test.restricted")),
                frozenset({"test.read"}),
            ),
        )
    )
    other_card = {**card, "name": "Outro agente"}
    other = TestClient(
        asgi_app(interfaces=AgentInterfaces(a2a=A2AConfig(other_card, diagnose, "other")))
    )
    disabled = TestClient(asgi_app(interfaces=AgentInterfaces()))
    card["skills"].clear()
    assert other.get("/.well-known/agent-card.json").json()["name"] == "Outro agente"
    assert other.post("/mcp/", json={}).status_code == 404
    assert disabled.get("/.well-known/agent-card.json").status_code == 404
    assert disabled.post("/a2a", json={}).status_code == 404
    assert disabled.post("/mcp/", json={}).status_code == 404

    def rpc(method, params):
        return {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}

    auth = {"X-A2A-Api-Key": "synthetic-a2a"}
    with TestClient(product, base_url="http://localhost:8000") as client:
        published = client.get("/.well-known/agent-card.json").json()
        assert published["name"] == "Agente sintético"
        assert published["skills"][0]["id"] == "synthetic"
        assert published["url"] == "https://agent.example/a2a"
        message = {"message": {"parts": [{"kind": "text", "text": "Incidente sintético"}]}}
        assert client.post("/a2a", json=rpc("message/send", message)).status_code == 401
        task = client.post("/a2a", json=rpc("message/send", message), headers=auth).json()["result"]
        assert task["status"]["state"] == "completed"
        lookup = rpc("tasks/get", {"id": task["id"]})
        assert client.post("/a2a", json=lookup, headers=auth).json()["result"] == task
        assert other.post("/a2a", json=lookup, headers=auth).json()["error"]["code"] == -32001

        headers = {
            "X-API-Key": "synthetic-mcp",
            "Accept": "application/json, text/event-stream",
        }
        assert client.post("/mcp/", json=rpc("tools/list", {})).status_code == 401
        response = client.post(
            "/mcp/",
            headers=headers,
            json=rpc(
                "initialize",
                {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {},
                    "clientInfo": {"name": "synthetic-client", "version": "0.1.0"},
                },
            ),
        )
        assert response.status_code == 200
        headers["Mcp-Session-Id"] = response.headers["Mcp-Session-Id"]
        headers["MCP-Protocol-Version"] = "2025-11-25"
        notice = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        assert client.post("/mcp/", headers=headers, json=notice).status_code == 202

        def mcp(method, params):
            reply = client.post("/mcp/", headers=headers, json=rpc(method, params))
            assert reply.status_code == 200
            if reply.headers["Content-Type"].startswith("application/json"):
                return reply.json()
            data = next(line[6:] for line in reply.text.splitlines() if line.startswith("data: "))
            return json.loads(data)

        tools = mcp("tools/list", {})["result"]["tools"]
        assert {item["name"] for item in tools} == {"echo", "restricted"}
        result = mcp("tools/call", {"name": "echo", "arguments": {"value": 42}})["result"]
        assert result.get("isError", False) is False
        denied = mcp("tools/call", {"name": "restricted", "arguments": {"value": 99}})["result"]
        assert denied["isError"]
        assert calls == [42]
