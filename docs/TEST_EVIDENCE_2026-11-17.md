# Evidência local de testes — 2026-11-17

Recuperação das execuções interrompidas durante a auditoria da separação de
IIC, FISC e Copilot Platform. Repositório canônico da suíte compartilhada:
Copilot Platform. Commit-base local 8da49972b532619be0beae027d64a764d0b461b6,
com alterações ainda não commitadas das etapas de distribuição e consumidores.
Este resultado não representa CI remota nem um novo release publicado.

## Resultados recuperados

| Escopo | Resultado | Evidência local |
|---|---|---|
| Seleção arquitetural na plataforma: findings, plugins, SDK, fronteiras e contratos | 47 passaram em 4,92 s | /tmp/platform-architecture-recovered.xml |
| Mesma seleção no snapshot IIC da auditoria | 47 passaram em 7,31 s | /tmp/iic-snapshot-architecture-recovered.xml |
| Suíte da plataforma com marcador not integration | 1938 passaram, 22 pulados, 17 desmarcados; 3 avisos; 142,57 s | /tmp/platform-unit-recovered.xml |
| Cobertura da suíte da plataforma | 82,68%; piso de 80% aprovado | /tmp/platform-recovery-coverage.json |
| Quality gate da plataforma | Aprovado; avisos de baseline antiga e vantagem não significativa de reranker candidato | /tmp/platform-recovery-quality.json |

O [resumo estruturado](TEST_EVIDENCE_2026-11-17.json) preserva resultados e hashes
SHA-256 dos relatórios JUnit. Os arquivos /tmp são locais e temporários; não
são links permanentes de distribuição. Logs detalhados: os mesmos nomes-base
com extensão .log, exceto o quality gate em /tmp/platform-recovery-quality.log.

A suíte usou Python 3.12.15 e pytest 9.2.0 do ambiente de desenvolvimento
existente em /tmp/copilot-platform-build/.venv. A implementação app foi carregada
do checkout canônico por PYTHONPATH explícito, não da cópia antiga usada para
provisionar esse ambiente. Essa execução não comprova instalação limpa a partir
do lock; a CI continua responsável por uv sync --locked em runner preparado.
Os testes pulados e desmarcados não contam como cobertura de infraestrutura real.

## Diagnóstico do bloqueio anterior

A reprodução com -vv e faulthandler_timeout=20 parou em
`test_endpoint_domain_plugins`, após 21 testes aprovados. O traceback mostrou
espera no portal de threads AnyIO/TestClient; o ambiente restrito também
reportou falha de criação de descritores. O limite de 60 segundos encerrou
essa execução, que não conta como aprovação.

A mesma seleção, fonte e interpretador passaram fora do sandbox autorizado,
sem mudança no código. A reprodução no snapshot IIC também passou nesse modo.
As evidências indicam interferência do ambiente restrito no teste HTTP, não
necessidade de trocar o comportamento da aplicação ou afrouxar asserts.
Traceback local: /tmp/platform-architecture-recovery.log.

## Modelo de deployment versus baseline

A baseline da plataforma registra qwen3.6:35b-a3b, medida em
2026-10-13T17:56:04.501Z. O manifesto Kyma do consumidor IIC no commit
4a4b0e4b71016402863e20d63b132d5261c8e360 declara provider openai e
modelo gpt-4o-mini. O comentário do manifesto descreve essa exceção cloud.
A configuração declarada não comprova qual modelo está ativo num cluster.

**Pendência:** medir o modelo cloud pelo pipeline de avaliação real do produto,
com acesso e credenciais próprios do ambiente autorizado, antes de atribuir a
ele resultados da baseline Qwen. Nenhuma inferência nova, regravação de digest
ou troca de modelo foi feita nesta recuperação. O baseline também permanece
com 34 dias de idade na data desta verificação.

O gate deployed_model_evaluated da plataforma retorna aprovação quando não há
manifesto Kyma no repositório. Portanto, seu PASS não comprova equivalência
entre o modelo cloud do produto e o modelo avaliado da plataforma. O IIC deve
manter essa comparação no escopo de seu deployment.

## Preservação futura

O workflow da plataforma foi ajustado para preservar quality gate JSON,
cobertura JSON e JUnit por 30 dias, inclusive em falha, e imprimir stacks de
testes sem progresso. A execução remota desses ajustes ainda está pendente.
O procedimento fica em [desenvolvimento](DEVELOPMENT.md).
