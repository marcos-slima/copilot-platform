# Plataforma compartilhada

A plataforma fornece bibliotecas, contratos e operações para IIC e FISC.
Não contém shells de produto, não é serviço remoto obrigatório e não copia
a implementação fiscal. Mantém capacidades SAP/SaaS/genéricas já existentes;
neutralidade de repositório não significa remoção das regras multivendor.

As versões são independentes: core Python 1.5.0, core-ui 0.1.1 e operações 1.0.2.
As migrations mantêm IDs e conteúdo; sua versão de distribuição é diferente
da versão do SDK. Combinações testadas são registradas no manifesto de build
e na configuração operations/component.toml.

A DA-96 define a transferência de propriedade dos gates. O core continua
verificando registro de conectores, Literals, CLI, supervisor, seed e admin.
O IIC verifica seu dropdown contra o schema do SDK; a plataforma executa
o consumidor contra o candidato. O FISC mantém suas validações de domínio.
Não houve alteração de prompt, roteamento, modelo, reranker ou política LLM.

A documentação operacional é inventariada em architecture/repository.toml.
Documentos e decisões herdados preservam o contexto histórico; referências
antigas a caminhos do monorepo não são instruções atuais de instalação.

Desenvolvimento: uv sync --all-packages --group dev --locked.
Executar scripts/quality_gate.py junto com a suíte. A publicação é manual e
somente promove artefatos de CI aprovado na main, sem rebuild.

O histórico relevante foi filtrado do IIC; autores, datas e mensagens foram
preservados com novos SHAs. O mapa de commits está em docs/history/commit-map.
O histórico original e as releases antigas do IIC permanecem disponíveis.
