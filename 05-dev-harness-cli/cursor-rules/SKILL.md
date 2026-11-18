---
name: cursor-rules
description: "Cria regras persistentes do Cursor em arquivos .mdc dentro de .cursor/rules/, escolhendo entre regra sempre ativa, por tipo de arquivo (globs) ou aplicada pelo agente conforme o contexto; use quando o usuário pedir para registrar uma convenção, padrão de código ou instrução permanente, ou mencionar .cursor/rules, .mdc ou AGENTS.md."
license: MIT
metadata: { author: "Akmon contributors" }
---

# Regras do Cursor (`.mdc`)

Regras dão contexto permanente ao agente do Cursor: ou valem sempre, ou só quando certos arquivos estão em jogo, ou o agente decide aplicá-las pela descrição.

## Quando usar

- "Crie uma regra para...", "registre esse padrão", "nossa convenção é...".
- Instruções que valem só para certos tipos de arquivo.
- Menção a `.cursor/rules/`, `.mdc` ou `AGENTS.md`.

Se o assunto já foi discutido na conversa, monte a regra com esse conteúdo sem perguntar de novo o que já foi respondido.

## Informações necessárias

1. **Finalidade:** o que a regra impõe ou ensina.
2. **Escopo:** sempre aplicar, ou só para arquivos específicos.
3. **Padrões de arquivo (globs)**, se o escopo for específico. Se o usuário citar arquivos mas não der padrões concretos, peça padrões concretos antes de gravar (use a ferramenta de perguntas estruturadas se existir; senão pergunte em texto).

## Passo a passo

1. Confirme finalidade, escopo e padrões. Escopo indefinido? Pergunte: "sempre aplicar ou só para arquivos específicos?".
2. Pedido com temas diferentes → **uma regra por tema**.
3. Garanta que `.cursor/rules/` existe (crie se faltar).
4. Crie `.cursor/rules/<nome>.mdc`, com nome descritivo em minúsculas e hífens.
5. Escreva o frontmatter e o corpo: título e instruções objetivas.
6. Inclua **exemplos concretos de uso incorreto e correto**, escritos para o caso real do usuário.
7. Confira o checklist.

## Formato

Arquivo `.cursor/rules/<nome>.mdc`. A extensão precisa ser `.mdc`: um `.md` simples nessa pasta é ignorado. Subpastas são aceitas (por exemplo `frontend/componentes.mdc`).

Frontmatter YAML entre linhas `---`:

| Campo | Tipo | Efeito |
|---|---|---|
| `description` | texto | descrição mostrada no seletor; é o que o agente lê para decidir aplicar |
| `globs` | texto | padrão de arquivo; a regra vale quando arquivos que casam estão em jogo (`**/*.ts`, `backend/**/*.py`) |
| `alwaysApply` | booleano | `true` aplica em toda sessão |

## Três configurações típicas

```markdown
---
description: Convenções de logging do serviço
alwaysApply: true
---
```

```markdown
---
description: Padrões para componentes React
globs: "**/*.tsx"
alwaysApply: false
---
```

```markdown
---
description: Como escrever migrações de banco neste projeto
---
```

1. **Sempre ativa:** `alwaysApply: true` e `description`, sem `globs`.
2. **Por arquivo:** `globs` preenchido e `alwaysApply: false`.
3. **Aplicada pelo agente conforme o contexto:** só `description` (sem `globs`, `alwaysApply` ausente ou diferente de `true`). Esse é o tipo que a skill `cursor-migracao-para-skills` consegue converter.

## Tamanho

- Ideal: uma regra curta (menos de ~50 linhas), um assunto.
- Limite prático: abaixo de 500 linhas. Regra grande → divida em várias.

## Alternativa

`AGENTS.md` na raiz do projeto: Markdown simples, sem frontmatter, para instruções gerais. Também aceito em subpastas, com precedência da mais específica.

## Exemplo de corpo (escrito para esta skill)

```markdown
# Tratamento de erros em handlers HTTP

- Sempre devolva o erro padronizado `{ codigo, mensagem }`.

Incorreto:
    return res.status(500).send(err.stack)

Correto:
    return res.status(500).json({ codigo: "ERRO_INTERNO", mensagem: "Falha ao processar" })
```

## Checklist antes de finalizar

- [ ] Arquivo `.mdc` dentro de `.cursor/rules/`.
- [ ] Frontmatter com os campos certos para o escopo.
- [ ] Menos de 500 linhas.
- [ ] Ao menos um exemplo incorreto/correto, quando o tema permitir.

## Resposta ao usuário

Nome do arquivo, escopo escolhido e os globs usados. A regra deve aparecer no seletor de regras com a descrição dada.

> ⚠️ Verificar na doc oficial: a lista de valores aceitos em `globs` (por exemplo, lista em vez de texto) não foi confirmada além dos exemplos acima. Consulte `https://cursor.com/docs/context/rules`.
