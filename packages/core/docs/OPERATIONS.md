# Operações da plataforma

O bundle copilot-operations tem versão própria em operations/component.toml.
Use o core da combinação testada no manifesto e execute Alembic a partir do
diretório extraído. Banco e credenciais são configuração do deployment;
o build não aplica migrations. IDs da cadeia permanecem os mesmos.

## Qualificação do bundle

A partir de operações 1.0.1, a CI aplica este diretório extraído em um banco
PostgreSQL descartável, usando o wheel candidato instalado fora do checkout.
Executa upgrade head, alembic check e as queries dos dashboards distribuídos.
A matriz repete essa validação com os ambientes instalados de IIC e FISC.
Isso valida os artefatos e commits testados; não aplica migrations nos bancos
dos produtos nem comprova inferência LLM ou execução em produção.

Para aplicar em um deployment autorizado, instale o core compatível registrado
no MANIFEST.json, configure DATABASE_URL e execute Alembic a partir deste
diretório: alembic -c alembic.ini upgrade head e alembic -c alembic.ini check.
Backup, permissões e plano de recuperação pertencem ao deployment.
