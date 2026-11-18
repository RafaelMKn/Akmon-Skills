# Contribuindo com o Akmon Skills

> **EN (summary):** Contributions are welcome. Small fixes and docs: open a PR directly. A **new skill** or a large change: open an issue first and wait for the `accepted` label. Every commit needs a DCO sign-off (`git commit -s`). Skills must come from real use, be sanitized (no secrets or client data) and fit an existing category. Scripts are allowed under the rules below and get a line-by-line human review. First response within 7 days. Issues and PRs in English are welcome.

Obrigado por querer contribuir. O Akmon é uma biblioteca **curada** de Agent Skills extraídas de operação real. Este guia explica o que aceitamos e como enviar.

## Antes de começar

| Quero... | Caminho |
|---|---|
| Tirar dúvida ou sugerir uma ideia em aberto | GitHub Discussions |
| Reportar um bug numa skill | Issue com o template **Bug** |
| Corrigir texto, link ou erro pequeno | PR direto |
| Propor uma **skill nova** ou mudança grande | Issue com o template **Nova skill** → espere a label `accepted` → PR |
| Reportar falha de segurança | **Não** abra issue. Veja [SECURITY.md](SECURITY.md) |

PR de skill nova sem issue aceita pode ser fechado com um pedido para abrir a issue antes. É para não fazermos você perder tempo.

## Régua para skill nova

Uma skill nova entra quando cumpre **todos** os itens:

1. **Uso real:** você a usou de verdade e descreve onde, no PR ou na issue.
2. **Formato válido:** pasta `<categoria>/<nome-da-skill>/` com `SKILL.md` e frontmatter YAML:
   ```yaml
   ---
   name: nome-da-skill          # igual ao nome da pasta, minúsculas e hífens
   description: "Use quando ... " # uma linha: quando o agente deve usar
   license: MIT
   author: Seu Nome (@seu-github)
   ---
   ```
3. **Sanitizada:** sem segredos, tokens, `.env`, e-mails, nomes de clientes ou dados pessoais.
4. **Cabe numa categoria existente** (`01-` a `06-`).
5. **Licença compatível:** conteúdo autoral seu sob MIT, ou de terceiros com licença permissiva (MIT, Apache-2.0, BSD), mantendo o `LICENSE` original na pasta e o crédito no `author`. Não aceitamos conteúdo sem licença ou com cláusula não comercial (NC).

## Regras para scripts

Skills podem trazer scripts (`scripts/`), porque agentes vão executá-los. Por isso:

- **Proibido:** baixar e executar código remoto (`curl … | bash`, `eval` de conteúdo baixado), ler ou enviar credenciais (`.env`, `~/.ssh`, tokens, keychain), código ofuscado ou minificado sem fonte, e comportamento diferente do que o `SKILL.md` descreve.
- **Esperado:** dependências declaradas, caminhos relativos à pasta da skill, nenhuma escrita fora do diretório de trabalho sem pedir, e um teste ou exemplo de execução quando possível.
- Todo PR com script passa por **revisão humana linha a linha**.

## Fluxo do PR

1. Faça fork e crie uma branch: `feat/<nome-da-skill>`, `fix/<assunto>` ou `docs/<assunto>`.
2. Commits no padrão [Conventional Commits](https://www.conventionalcommits.org/pt-br/) (`feat:`, `fix:`, `docs:`, `ci:`, `chore:`).
3. **Assine cada commit (DCO):** `git commit -s`. Isso adiciona `Signed-off-by: Nome <email>` e declara que você tem direito de enviar a contribuição ([Developer Certificate of Origin](https://developercertificate.org/)).
4. Um assunto por PR: não misture skill nova com mudança de CI ou de documentação geral.
5. Não edite contagens nem tabelas dos READMEs à mão se o PR não for sobre elas, para evitar conflito com outros PRs.
6. Preencha o template do PR.

### O que acontece depois

- O CI valida frontmatter, links, segredos e scripts. Só revisamos PRs com o CI verde.
- Um agente faz a pré-revisão técnica e de segurança, e um mantenedor humano decide e faz o merge.
- O merge é sempre **squash**.
- **Primeira resposta em até 7 dias.** A triagem é semanal.
- Issue ou PR em `needs-info` sem resposta por 30 dias é fechado, com aviso no dia 23. Dá para reabrir quando quiser.

## Labels

| Grupo | Labels |
|---|---|
| Tipo | `bug`, `new-skill`, `skill-fix`, `docs`, `ci` |
| Status | `needs-triage`, `needs-info`, `accepted`, `wontfix`, `duplicate` |
| Área | `area:01-automacao` … `area:06-produtividade` |

## Crédito

Quem contribui aparece no campo `author` do frontmatter da skill e na seção **Contribuidores** do README.

## Licença

Ao contribuir, você concorda que sua contribuição autoral é licenciada sob a [MIT](LICENSE). Conteúdo de terceiros mantém a licença original; veja [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
