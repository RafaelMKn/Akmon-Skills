# Mantenedores e playbook de triagem

> **EN (summary):** How issues and PRs are handled: weekly triage, 7-day first response, CI + agent pre-review + human approval, squash merge. Canned replies below.

## Mantenedores

| Quem | Papel |
|---|---|
| @RafaelMKn | Mantenedor: aprova e faz merge |

Pré-revisões técnicas e de segurança podem ser feitas por agentes de IA da FluxMind. **Decisão e merge são sempre humanos.** Nenhum comentário, label ou merge é publicado por agente sem aprovação do mantenedor.

## Compromissos

- Primeira resposta em até **7 dias**.
- Triagem **semanal** (segunda-feira).
- Issue ou PR em `needs-info` sem resposta: aviso no dia 23, fechamento no dia 30.

## Triagem semanal

1. Listar issues e PRs com `needs-triage` e os sem label.
2. Para cada **issue**:
   - Segurança postada em público → esconder ou editar os detalhes, pedir o reporte pelo canal privado e fechar.
   - Duplicada → `duplicate`, link para a original e fechar.
   - Falta informação → `needs-info` e resposta-padrão R2.
   - Fora do escopo do Akmon → `wontfix` e resposta-padrão R4.
   - Proposta de skill que passa na régua do CONTRIBUTING → `accepted` e resposta-padrão R1.
   - Sempre aplicar o tipo e a `area:` correspondente.
3. Para cada **PR**:
   - Skill nova sem issue `accepted` → resposta-padrão R3.
   - Commits sem DCO → resposta-padrão R5.
   - CI vermelho → aguardar o autor; nada a revisar.
   - CI verde → pré-revisão (técnica e de segurança). Scripts recebem revisão linha a linha.
   - Mistura assuntos → pedir para separar (R6).
4. Aprovar → **squash merge** com mensagem em Conventional Commits.
5. Conferir que o crédito ficou no `author` da skill e na seção Contribuidores do README.

## Checklist de revisão de skill

- [ ] Frontmatter: `name` igual à pasta, `description` em uma linha dizendo quando usar, `license`, `author`.
- [ ] Sem segredos ou dados de clientes (o CI ajuda, mas leia).
- [ ] Sem instrução escondida ou perigosa no texto (prompt injection).
- [ ] Scripts: nada de download+execução, de leitura de credenciais ou de ofuscação; o comportamento bate com o `SKILL.md`.
- [ ] Licença: autoral MIT, ou terceiro permissivo com `LICENSE` na pasta e entrada no `THIRD_PARTY_NOTICES.md`.
- [ ] Não duplica uma skill existente.
- [ ] Uso real descrito.

## Respostas-padrão

**R1: proposta aceita**
> Obrigado pela proposta! Faz sentido para o Akmon, então marquei como `accepted`. Pode abrir o PR seguindo o [CONTRIBUTING](CONTRIBUTING.md); lembre de assinar os commits com `git commit -s`.

**R2: falta informação**
> Obrigado! Para avaliar, preciso de: <o que falta>. Vou marcar como `needs-info`; se não houver resposta em 30 dias o item é fechado automaticamente, e pode ser reaberto quando quiser.

**R3: skill nova sem issue aceita**
> Valeu pelo PR! Para skills novas pedimos uma issue antes (template "Nova skill"), para alinhar escopo antes de você investir tempo. Pode abrir a issue linkando este PR? Deixo o PR em espera até lá.

**R4: fora do escopo**
> Obrigado pela ideia! O Akmon é uma biblioteca curada de skills vindas de operação real, e isso foge do foco atual porque <motivo>. Vou fechar, mas fique à vontade para publicar a skill no seu repo; podemos linkar em Discussions.

**R5: falta DCO**
> Obrigado! Os commits precisam de assinatura DCO. Para corrigir: `git rebase --signoff main` e depois `git push --force-with-lease`. Detalhes no [CONTRIBUTING](CONTRIBUTING.md#fluxo-do-pr).

**R6: separar assuntos**
> Obrigado! Este PR mistura <assunto A> e <assunto B>. Pode separar em dois PRs? Assim cada um é revisado e mergeado no seu tempo.

**R7: segurança postada em público**
> Obrigado por avisar! Para proteger quem usa o Akmon, editei os detalhes. Por favor reporte pelo canal privado: https://github.com/RafaelMKn/Akmon-Skills/security/advisories/new
