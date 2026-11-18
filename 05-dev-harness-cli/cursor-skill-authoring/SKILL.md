---
name: cursor-skill-authoring
description: "Guia a criação de skills de agente para o Cursor (pasta com SKILL.md, frontmatter, descrição, corpo e arquivos de apoio); use quando o usuário quiser criar uma skill, transformar um fluxo recorrente em skill, entender o formato do frontmatter ou decidir onde guardar uma skill pessoal ou de projeto."
license: MIT
metadata: { author: "Akmon contributors" }
---

# Criando skills para o Cursor

Uma skill é uma pasta com um `SKILL.md` obrigatório e arquivos de apoio opcionais. Quanto melhor o nome, a descrição e o corpo, mais certeiro o agente ao escolher e seguir a skill.

## Quando usar

- Criar uma skill nova ou transformar um fluxo repetido em skill.
- Dúvidas sobre o formato do `SKILL.md` ou do frontmatter.
- Escolher entre skill pessoal e de projeto.

Se a conversa já trouxe o fluxo, use esse conteúdo sem repetir perguntas.

## Informações necessárias

- Tarefa ou fluxo que a skill cobre.
- **Local:** pessoal ou de projeto (pergunte se não estiver claro).
- Gatilhos: quando o agente deve aplicá-la sozinho.
- Conhecimento de domínio que o agente não tem por padrão.
- Formato de saída esperado, exemplos e convenções existentes.
- Se haverá scripts.

**Nunca grave em `~/.cursor/skills-cursor/`**: pasta reservada ao produto.

## Locais

| Escopo | Pasta | Alcance |
|---|---|---|
| Pessoal | `~/.cursor/skills/<nome>/` (também `~/.agents/skills/`) | todos os projetos |
| Projeto | `.cursor/skills/<nome>/` (também `.agents/skills/`) | vai para o repositório |

A identidade da skill vem da pasta que contém o `SKILL.md`, não de subpastas de categoria.

## Passo a passo

1. Reúna os requisitos acima.
2. **Texto fornecido pelo usuário:** se ele deu o texto exato da skill, use-o palavra por palavra no `SKILL.md`, sem reescrever, melhorar ou envolver em cabeçalhos/comentários.
3. Escolha o local e crie a pasta.
4. **Nome:** minúsculas, números e hífens; deve coincidir com o nome da pasta; evite genéricos ("helper", "utils"). Limite de 64 caracteres.
5. **Descrição:** terceira pessoa, dizendo o que a skill faz **e quando usá-la**, com termos que o usuário costuma empregar. Até 1024 caracteres.
6. **Frontmatter:** inclua `disable-model-invocation: true` por padrão, para a skill só carregar quando chamada explicitamente (`/nome`). Omita só se o agente deve invocá-la sozinho.
7. **Corpo:** passos claros, exemplos concretos e checklist quando houver etapas. Só o que o agente ainda não sabe.
8. **Detalhes longos** vão para arquivos de apoio ligados direto do `SKILL.md`, sem níveis extras de indireção.
9. **Scripts:** resolva o problema no script em vez de deixar para o agente; documente pacotes necessários, trate erros com mensagem clara e diga se o agente deve **executar** ou apenas **ler** o script.
10. Confira o checklist final.

## Frontmatter

| Campo | Regra |
|---|---|
| `name` | obrigatório; minúsculas, números e hífens; igual ao nome da pasta |
| `description` | obrigatória; não vazia |
| `disable-model-invocation` | booleano; `true` = só uso explícito via `/nome` |
| `paths` | opcional; padrões de arquivo (lista ou texto separado por vírgula); o antigo `globs` ainda é aceito |
| `metadata` | opcional; pares chave-valor livres |

## Estrutura da pasta

```
<nome>/
├── SKILL.md        # obrigatório
├── references/     # documentação carregada sob demanda
├── scripts/        # executáveis
└── assets/         # modelos, imagens, dados
```

Arquivos de apoio com um único nível de profundidade a partir do `SKILL.md`. Padrões de corpo úteis estão em `references/padroes.md`.

## Anti-padrões

- Caminhos com barra invertida (use `/`).
- Muitas alternativas sem uma recomendação padrão.
- Informação com prazo de validade.
- Termos que mudam entre seções (escolha um e mantenha).
- Nomes vagos.

## Checklist final

- [ ] Descrição específica, em terceira pessoa, com o quê e quando.
- [ ] Corpo com menos de 500 linhas.
- [ ] Nome e descrição dentro dos limites.
- [ ] Terminologia consistente.
- [ ] Referências com um nível.
- [ ] Nada com prazo de validade.
- [ ] Scripts testados, se houver.

## Resposta ao usuário

Caminho criado, nome da skill, se a invocação é automática ou explícita e **o que não foi testado**. Sucesso = a skill aparece na lista de skills do Cursor e é encontrada pela descrição em um pedido de teste.

> ⚠️ Verificar na doc oficial: os limites de 64 caracteres (nome), 1024 (descrição) e 500 linhas (`SKILL.md`) vêm da especificação interna e não aparecem na página de skills do Cursor consultada. A reserva de `~/.cursor/skills-cursor/` também não está documentada; trate como proibição por cautela. Se houver ferramenta de perguntas estruturadas no ambiente, prefira-a, mas não dependa dela. Fonte: `https://cursor.com/docs/context/skills`.
