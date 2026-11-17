# Desenvolvimento da plataforma

Requisitos: Python 3.12, uv 0.13.4, Node.js 22 e ferramentas nativas de compilação
(CMake, make, gcc, pkg-config, libssl-dev, libffi-dev, libsasl2-dev no Linux).
A raiz é um workspace virtual uv; não é um produto FastAPI a ser instalado.

~~~bash
uv sync --all-packages --group dev --locked
npm ci --ignore-scripts
uv run python scripts/quality_gate.py
uv run pytest tests/ -m "not integration" -q --tb=short --cov=app --cov-fail-under=80
npm test
~~~

O SDK é app.sdk e a implementação está em packages/core/src/app. O core-ui
está em packages/core-ui. Não instalar IIC/FISC dentro do workspace para ocultar
recursos ausentes. O namespace app é fornecido por copilot-core.

A CI adiciona PostgreSQL para migrations/queries, Qdrant para RAG e Neo4j para
GraphRAG; esses serviços não são iniciados pelos comandos acima. Testes opcionais
podem ser pulados sem infraestrutura. O gate deve acompanhar a suíte, sem substituir testes.
Prompts e digests não mudam por organização documental; re-baseline exige medição real.

Artefatos isolados são construídos e verificados por scripts/build_shared_distribution.py
e scripts/verify_shared_distribution.py. consumers.json fixa commits de produtos
para testes de compatibilidade candidatos; a CI de produto continua independente.
Veja [distribuição](../packages/core/docs/DISTRIBUTION.md) e [releases](RELEASES.md).

O inventário architecture/repository.toml delimita os guias operacionais auditados
pelos gates de markup/código/variáveis; não representa validação semântica de
cada parágrafo histórico. O mapa DOCUMENTATION_MAP.json explicita essa separação.
