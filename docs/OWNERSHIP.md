# Propriedade e preservação dos testes

| Responsável | Código e verificações atuais |
|---|---|
| Copilot Platform | SDK, grafo, gateway, RAG, evidências, auth, conectores, core-ui; testes funcionais e invariantes em tests/; migrations e queries de dashboards |
| IIC | Shell Python e UI de integração, catálogo de transportes versus contrato público do SDK, imagem e manifests do produto |
| FISC | Domínio fiscal, contratos NF-e, XML/XSD, UI, testes e imagem do produto |

Os produtos consomem releases por versão e hash. A CI da plataforma testa também
commits fixados dos dois consumidores em consumers.json, com wheel, tarball de UI
e bundle operacional candidatos;
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

## Matriz completa de candidatos

Os jobs consumer_iic e consumer_fisc verificam checksums e a combinação declarada
entre operações e core antes de clonar o produto. Em um checkout temporário do
commit fixado, substituem as dependências Python e UI e as três entradas do
manifesto shared-libraries.json pelos artefatos candidatos e seus hashes.
Os locks temporários são resolvidos somente nessa cópia; o produto não é alterado.

Cada consumidor constrói UI e wheel, instala o produto e usa seu próprio script
fetch_operations.py para verificar e extrair o bundle candidato. Com o Python do
consumidor em modo isolado e o core instalado, a matriz executa upgrade head,
alembic check e queries extraídas em um banco exclusivo e descartável. Por fim,
executa os testes do produto. Não usa fontes do core do checkout da plataforma.

O modo --postgres exige OPERATIONS_TEST_DATABASE_URL e está habilitado nos dois
jobs. O banco indicado é usado para criar e remover o banco temporário, sem
receber as migrations. Sem essa opção o relatório registra operações como
not-run; esse resultado não representa a matriz completa exigida na CI.

Após sucesso, cada job publica consumer-iic.json ou consumer-fisc.json com o
commit do consumidor, commit de origem dos artefatos, versões, hashes e resultados.
As URLs file desses relatórios identificam entradas temporárias do teste, não
canais permanentes de instalação. A versão e o hash são a referência do artefato.
A publicação de componentes exige sucesso dos dois jobs pela política de promoção.

A matriz comprova compatibilidade dos commits fixados com os artefatos testados.
Não comprova todos os commits futuros dos produtos, build de suas imagens,
inferência real ou homologação fiscal. Essas verificações mantêm seus próprios
pipelines e evidências.
