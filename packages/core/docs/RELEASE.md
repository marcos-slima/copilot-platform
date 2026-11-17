# Publicar um componente compartilhado

A publicação usa assets GitHub Releases de Copilot Platform, sem exigir registry
privado. Core, core-ui e operações não precisam receber release conjunta.

1. Alterar o manifest somente do componente necessário, revisar compatibilidade
   e contratos, e executar as validações descritas em [desenvolvimento](../../../docs/DEVELOPMENT.md).
2. Integrar a mudança e aguardar Platform CI aprovado na main, incluindo
   distribuição e consumidores. Os artefatos precisam ter source_dirty=false.
3. Executar o workflow manual Publish component, indicando componente
   (`core`, `core-ui` ou `operations`) e run_id aprovado.
4. O publicador confere origem/main, sucesso, versões e checksums; promove os
   bytes já testados, cria draft, verifica os assets e publica a tag específica.
   Uma versão existente é recusada; não mover tags nem sobrescrever assets.
5. Atualizar o consumidor por PR, com URL/hash/locks, testes de produto e imagem.

A cadeia de migrations não é renumerada quando muda a versão do bundle.
Operações declaram combinações testadas em operations/component.toml;
versão de distribuição não equivale a uma revisão de schema.
A publicação não aplica migrations nem implanta produtos.

[Política SemVer e versões](../../../docs/RELEASES.md) · [Distribuição](DISTRIBUTION.md)
· [Contratos](CONTRACTS.md).
