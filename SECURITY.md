# Política de Segurança / Security Policy

> **EN:** Do not open public issues for security problems. Report privately via GitHub: **Security → Report a vulnerability** (https://github.com/RafaelMKn/Akmon-Skills/security/advisories/new). First response within 7 days.

## Como reportar
Não abra issue pública. Use o canal privado do GitHub:
**Security → Report a vulnerability** — https://github.com/RafaelMKn/Akmon-Skills/security/advisories/new

Primeira resposta em até 7 dias.

## O que reportar
Skills são instruções que agentes de IA executam. Considere vulnerabilidade, entre outros:
- Prompt injection ou instruções escondidas em `SKILL.md`, references ou exemplos.
- Scripts que baixam e executam código remoto (ex.: `curl | bash`), leem ou enviam credenciais, `.env`, chaves SSH ou tokens.
- Código ofuscado ou comportamento diferente do descrito na skill.
- Segredos ou dados pessoais/de clientes commitados.
- Falhas nos workflows do GitHub Actions (vazamento de secrets, execução de código de fork com permissões).

## Escopo
Todo o conteúdo deste repositório, incluindo skills de terceiros listadas em `THIRD_PARTY_NOTICES.md`. Falhas no projeto de origem de uma skill de terceiros também devem ser reportadas ao autor original.

## Como tratamos
1. Confirmamos o recebimento e avaliamos a severidade.
2. Corrigimos ou removemos a skill afetada.
3. Publicamos um security advisory quando aplicável, com crédito a quem reportou (se desejar).
