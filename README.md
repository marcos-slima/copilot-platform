# Copilot Platform

Plataforma compartilhada de diagnóstico para IIC e FISC.
Core Python, core-ui e operações têm versões independentes.

| Componente | Versão | Conteúdo |
|---|---|---|
| copilot-core | 1.5.0 | SDK, grafo, gateway, RAG, evidências, auth e conectores |
| @copilot/core-ui | 0.1.1 | ESM, tipos e CSS compartilhados |
| copilot-operations | 1.0.2 | Migrations e dashboards, candidato para core 1.5.0 |

Os produtos permanecem em repositórios próprios:
[IIC](https://github.com/marcos-slima/integration-incident-copilot) e
[FISC](https://github.com/marcos-slima/fiscal-incident-support-copilot).
Este repositório não é uma aplicação de produto nem um serviço remoto obrigatório.

Comece pelo [índice documental](docs/README.md).

Veja [arquitetura](docs/PLATFORM.md), [releases](docs/RELEASES.md),
[propriedade](docs/OWNERSHIP.md) e [operação](operations/README.md).

## Desenvolvimento

~~~bash
uv sync --all-packages --group dev --locked
npm ci
uv run python scripts/quality_gate.py
uv run pytest tests/ -m "not integration" -q --cov=app --cov-fail-under=80
npm test
~~~

## Grafo compartilhado

<!-- grafo-gerado:inicio (scripts/graph_diagram.py --write; nao editar a mao) -->

**Default: GRAPH_RAG_ENABLED=false**

```mermaid
flowchart TD
    inicio(["run_diagnosis"])
    supervisor["supervisor<br/>classify_domain: sap / saas / generic<br/>(deterministic, no LLM)"]
    connector["connector<br/>get_connector(interface_type).fetch(identifier)<br/>real system or demo scenario"]
    retrieve["retrieve<br/>hybrid RAG + reranker<br/>(reference_library fallback)"]
    sap_diagnose["sap_diagnose<br/>rule engine; else LLM via gateway<br/>+ guardrails + evidence"]
    saas_diagnose["saas_diagnose<br/>rule engine; else LLM via gateway<br/>+ guardrails + evidence"]
    generic_diagnose["generic_diagnose<br/>rule engine; else LLM via gateway<br/>+ guardrails + evidence"]
    report["report<br/>Markdown report"]
    fim(["DiagnosisResponse<br/>+ escalation (DA-44)<br/>+ record_incident"])
    inicio --> supervisor
    connector --> retrieve
    generic_diagnose --> report
    report --> fim
    retrieve -.->|"generic"| generic_diagnose
    retrieve -.->|"saas (default)"| saas_diagnose
    retrieve -.->|"sap"| sap_diagnose
    saas_diagnose --> report
    sap_diagnose --> report
    supervisor --> connector
```

<!-- grafo-gerado:fim -->
