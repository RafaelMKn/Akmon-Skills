---
name: cursor-migracao-para-skills
description: "Converte regras do Cursor aplicadas pelo agente (.mdc sem globs e sem alwaysApply) e comandos de barra (.md) para skills (SKILL.md em pasta própria), preservando o corpo do texto e trocando só o frontmatter; use quando o usuário quiser migrar regras ou comandos para skills ou unificá-los na pasta de skills."
license: MIT
metadata: { author: "Akmon contributors" }
---

# Migração de regras e comandos para skills (Cursor)

Converte dois tipos de arquivo para o formato de skill. **O corpo do texto não muda; só o frontmatter.**

> O Cursor traz uma skill embutida `/migrate-to-skills` que faz esta conversão. Se o usuário a tiver disponível, mencione-a como alternativa; esta skill serve quando ele quer o processo guiado, com conferência e desfazer.

## Quando usar

- Migrar regras ou comandos para skills.
- Converter `.mdc` em `SKILL.md`.
- Reunir comandos na pasta de skills.

## Origens e destinos

| Escopo | Origem | Destino |
|---|---|---|
| Projeto | `.cursor/rules/*.mdc` (inclusive subpastas) e `.cursor/commands/*.md` | `.cursor/skills/` |
| Usuário | `~/.cursor/commands/*.md` | `~/.cursor/skills/` |

Pergunte o escopo (projeto, usuário ou ambos). Crie as pastas de destino que faltarem.

## O que migrar

**Regras:** somente as que têm `description`, **não** têm `globs` e **não** têm `alwaysApply: true`. As demais ficam como estão.

**Comandos:** todos (não têm frontmatter).

Ignore qualquer caminho dentro de `~/.cursor/worktrees` e `~/.cursor/skills-cursor`. Regras de usuário que não estão no sistema de arquivos não são migradas.

## Passo a passo

1. Crie as pastas de destino.
2. Liste os candidatos pelos critérios acima e mostre a lista ao usuário.
3. **Regra → skill:** crie a pasta com o nome do arquivo sem `.mdc`; escreva `SKILL.md` com frontmatter contendo `name` e `description` (sem `globs`, sem `alwaysApply`); copie o corpo que vem depois do frontmatter original **caractere por caractere**, preservando espaços, quebras de linha e blocos de código.
4. **Comando → skill:** crie a pasta com o nome do arquivo sem `.md`; defina `description` pelo primeiro título (sem o `#`) ou, se o título não servir, infira do conteúdo e **mostre a inferência ao usuário antes de gravar**; frontmatter com `name`, `description` e `disable-model-invocation: true`; linha em branco; depois o conteúdo original inteiro.
5. **Verifique** cada skill criada: corpo idêntico ao original (compare depois de remover o frontmatter).
6. **Apagar originais:** só depois de verificar que a skill nova existe e está completa **e** com confirmação explícita do usuário. Sem confirmação, liste-os como mantidos.
7. Responda com a lista: origem, destino e situação (criada, pulada, erro). Informe que a migração pode ser desfeita e ofereça.
8. **Desfazer** (só com confirmação): recrie cada original a partir do corpo da skill (sem frontmatter) e remova a pasta criada.

Leia e escreva arquivos com as ferramentas de arquivo, não pelo terminal. Se houver delegação a subagentes, dá para paralelizar por categoria (regras do projeto, comandos do usuário, comandos do projeto).

## Frontmatter

Regra (origem): `description`, `globs`, `alwaysApply`.

Skill (destino):

- `name`: nome da pasta; minúsculas, números e hífens.
- `description`: o que a skill faz.
- `disable-model-invocation: true`: para comandos, para que só o usuário os acione pelo menu de barra.

## Critério de sucesso

- Nenhuma origem apagada sem verificação.
- Nenhum corpo alterado.
- Nenhum arquivo fora das pastas indicadas tocado.
- Falha em uma origem não interrompe as demais: registre o erro na lista.

> ⚠️ Verificar na doc oficial: a página de skills do Cursor confirma a migração para `.cursor/skills/` e o critério das regras; a migração de comandos de **usuário** para `~/.cursor/skills/` vem da especificação interna e não foi confirmada. Fonte: `https://cursor.com/docs/context/skills`.
