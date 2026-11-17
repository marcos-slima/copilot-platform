# Releases independentes

| Componente | Versão inicial nesta plataforma | Tag | Artefatos |
|---|---|---|---|
| copilot-core | 1.4.1 | core/v1.4.1 | wheel e sdist |
| @copilot/core-ui | 0.1.1 | core-ui/v0.1.1 | tarball npm com ESM/tipos/CSS |
| copilot-operations | 1.0.0 | operations/v1.0.0 | Alembic, dashboards e validador |

As três releases iniciais estão [publicadas](https://github.com/marcos-slima/copilot-platform/releases).
Para novas versões, manifest não comprova publicação. Não existe versão única da plataforma.
Operações têm matriz explícita de core testado; atualizar compatibilidade
também exige validação, sem renumerar revisões do banco.

Publicação: workflow manual Publish component, selecionando componente e run
aprovado da main. O publicador confere hashes, commit limpo e versão, e falha
se a tag já existir. Apenas o componente selecionado ganha release.
Não substituir bytes ou mover tags publicadas. Para correção, incrementar
patch; para adição compatível, minor; para ruptura de contrato estável, major.
Core-ui segue 0.y.z: mudanças incompatíveis exigem incremento minor e migração.

CI inclui suíte com cobertura >=80%, quality gate, migrations/dashboards,
RAG com Qdrant e GraphRAG com Neo4j. Artefatos são testados fora do checkout
e pelos consumidores em commits fixados em consumers.json.
A instalação em produto usa URL e hash nos seus locks; cada produto atualiza
separadamente. As versões antigas continuam no IIC para builds anteriores.

Os nomes copilot-core, app.sdk e @copilot/core-ui são preservados.
A distribuição inicial usa GitHub Release assets; não há publicação PyPI/npm
nem propriedade de scope npm presumida. O tarball continua private para
evitar publicação acidental em registro.

Migrações não são aplicadas pelo build. Não há deploy de produção, inferência
LLM real ou homologação fiscal implícitos na publicação de uma biblioteca.

## Operações 1.0.1

Patch preparado para qualificação por artefato: valida migrations e dashboards
extraídos com wheel instalado e nos dois consumidores, preservando evidências
de testes. O manual do bundle descreve esse alcance. Não altera IDs ou conteúdo
das migrations, prompts ou implementação do core/UI. Mantém compatibilidade
com core 1.4.1. A publicação ocorre somente após CI aprovada na main; esta nota
não comprova que a tag operations/v1.0.1 já tenha sido publicada.
