# Propriedade e preservação dos testes

| Responsável | Código e verificações atuais |
|---|---|
| Copilot Platform | SDK, grafo, gateway, RAG, evidências, auth, conectores, core-ui; testes funcionais e invariantes em tests/; migrations e queries de dashboards |
| IIC | Shell Python e UI de integração, catálogo de transportes versus contrato público do SDK, imagem e manifests do produto |
| FISC | Domínio fiscal, contratos NF-e, XML/XSD, UI, testes e imagem do produto |

Os produtos consomem releases por versão e hash. A CI da plataforma testa também
commits fixados dos dois consumidores em consumers.json, com wheels/tarballs candidatos;
a CI de cada produto valida seus locks, distribuição e imagem de forma independente.

## Migração dos testes do antigo monorepo

- test_kyma_manifests.py, test_local_overlay.py e test_bloco3_infra.py: verificações de implantação/topologia do IIC, preservadas em docs/history/iic-test-ownership. Precisam acompanhar alterações dos manifests do produto; não contam como cobertura do core.
- test_diagramas.py: verificações do grafo compartilhado continuam ativas. As quatro verificações específicas de Compose, Kyma e workflows de produto foram preservadas no arquivo original em history/iic-test-ownership.
- test_bloco5_docs.py: política Kyma de fallback transferida para tests/test_deployment_policy.py do IIC; verificações de regras/conectores continuam na plataforma.
- test_skill_registry.py: a antiga verificação de COPY no Dockerfile do produto foi substituída pela inclusão obrigatória de skills no wheel do core.
- test_da95_boundaries.py e test_i18n_content.py: verificações locais cobrem core e core-ui; a ausência de produtos não é interpretada como código existente. UI e traduções de produto são verificadas nos consumidores.
- scripts de CI específicos da antiga topologia estão preservados em docs/history/product-ci. A distribuição neutra e seus testes de operações permanecem ativos em scripts/.

Documentação herdada é evidência histórica das decisões. Somente os documentos
no inventário architecture/repository.toml são instruções atuais da plataforma.
O mapa docs/history/commit-map relaciona os commits originais aos commits filtrados;
a extração não altera o histórico publicado nos repositórios de origem.
