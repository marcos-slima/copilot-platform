# Copilot Platform

Manter copilot-core, app.sdk e @copilot/core-ui. Usar uv, não pip/poetry.
Nunca importar produtos no core; contratos são HTTP/SDK 1.0 e plugin 1.1.
Preservar os invariantes históricos em CLAUDE.md e as decisões em docs/DECISOES_DE_ARQUITETURA.md.
Reranker fixo mmarco; rule engine ativo, classificação determinística,
MCP e correlação fail-closed; evidência não depende de autoavaliação LLM.
Prompts exigem re-baseline real quando o texto muda. Não regravar digest para passar teste.
Gate roda junto com a suíte. O perfil DA-96 escopa apenas a documentação
operacional e delega dropdown de produto aos seus testes de contrato.
Sem dados ou credenciais reais. Regras e migrations mantêm IDs e hashes.
