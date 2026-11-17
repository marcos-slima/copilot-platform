# Operações

Componente copilot-operations, com versão própria em component.toml.
A cadeia canônica está em ../alembic, ../alembic.ini e os dashboards em
../deploy/grafana/dashboards. IDs de revisão não foram renumerados.
Instalar o core compatível antes de aplicar migrations em banco autorizado.
A versão do bundle é independente do SDK; a matriz registra combinações testadas.

## Validação pelo artefato

A CI de distribuição verifica checksums e compatibilidade, instala o wheel
candidato em diretório temporário e extrai o bundle fora do checkout. O comando
abaixo cria um banco exclusivo, aplica upgrade head, executa alembic check e
valida as queries usando o script e os dashboards extraídos:

```bash
uv run python scripts/verify_shared_distribution.py dist/shared --postgres
```

Configure OPERATIONS_TEST_DATABASE_URL em ambiente para uma instância de teste
PostgreSQL 16 com permissão de criar bancos. O banco indicado pela URL é usado
somente para administração: as migrations rodam em um banco novo, com nome
aleatório, removido ao finalizar, inclusive em falha de validação. Uma interrupção
forçada do processo pode exigir remoção manual desse banco temporário.
O upload dos artefatos ocorre somente após essa validação passar.

Sem --postgres, o comando mantém apenas a inspeção e o smoke de importação.
As dependências de terceiros são reutilizadas do ambiente; o teste não comprova
resolução de dependências em sistema limpo. Não executa migrations em bancos dos
produtos e não substitui a matriz de consumidores.
