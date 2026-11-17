# Distribuição independente das bibliotecas

A fonte canônica é Copilot Platform. Os três componentes têm versões próprias:

| Componente | Manifest | Artefato público |
|---|---|---|
| copilot-core 1.4.1 | packages/core/pyproject.toml | wheel/sdist em core/v1.4.1 |
| @copilot/core-ui 0.1.1 | packages/core-ui/package.json | tarball em core-ui/v0.1.1 |
| copilot-operations 1.0.0 | operations/component.toml | tar.gz em operations/v1.0.0 |

As releases estão no [repositório da plataforma](https://github.com/marcos-slima/copilot-platform/releases).
Não há publicação PyPI/npm neste fluxo; não se presume controle do scope npm.
`private: true` impede publicação npm acidental, sem impedir consumo por tarball.

Na raiz da plataforma, após instalar o workspace conforme [desenvolvimento](../../../docs/DEVELOPMENT.md):

~~~bash
uv run python scripts/build_shared_distribution.py --out-dir dist/shared
uv run python scripts/verify_shared_distribution.py dist/shared
~~~

Use diretório de saída novo/vazio. O builder constrói wheel/sdist somente das
fontes do core, compila/empacota o core-ui e gera operações por allowlist.
distribution.json registra versões independentes, commit, source_dirty e hashes;
SHA256SUMS inclui o manifesto. Candidato local sujo não é publicação aprovada.

O verificador confere recursos, identidade, hashes e instalação isolada. O core
inicializa sem fontes de IIC/FISC. A CI testa commits fixados dos consumidores
contra wheel/tarball candidatos; não instala fontes dos produtos dentro do core.
O bundle inclui Alembic, revisões completas, dashboards e validador de queries,
com MANIFEST.json e combinação de core testada. Não inclui credenciais nem corpus fiscal.

Produtos declaram URL/versionamento explícitos e seus próprios uv.lock e lock npm;
shared-libraries.json registra também hashes e origem. O IIC e o FISC atualizam
separadamente. Nunca copiar fontes do core para um consumidor.
Veja [contratos](CONTRACTS.md), [publicação](RELEASE.md) e [operações](OPERATIONS.md).
