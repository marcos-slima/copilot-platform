# Copilot Core

Biblioteca Python compartilhada 1.4.1. Imports públicos de produto usam app.sdk.
O core não importa IIC ou FISC. Contratos HTTP/SDK 1.0 e plugin 1.1.
O pacote inclui templates, traduções, ontologia e skills.

Construção: uv build --package copilot-core --wheel --sdist.
Teste e gate são executados da raiz da plataforma. Operações têm versão própria.
O namespace app é exclusivo deste pacote; consumidores instalam o wheel.
