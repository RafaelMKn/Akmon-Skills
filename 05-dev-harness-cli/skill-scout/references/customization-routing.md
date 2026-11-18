# Qual tipo de customização usar?

Antes de buscar uma skill, confirme que uma skill é mesmo a resposta.

| O usuário quer... | Use | Por quê |
|---|---|---|
| Um comando de barra simples, um atalho para um texto | **Prompt** | não precisa de arquivos nem de gatilho |
| Orientação que vale sempre, ou só para certos arquivos | **Instrução** (regra) | contexto permanente, curto |
| Persona, limites de ferramenta ou delegação de tarefas | **Agente** | define quem faz e com quais ferramentas |
| Garantia **determinística** (sempre bloquear, sempre formatar, auditar) | **Hook** | roda código em eventos, sem depender do modelo |
| Um pacote reutilizável com referências, scripts ou modelos | **Skill** | carrega sob demanda, pelo nome e descrição |

Regra prática: se o modelo "pode esquecer" e isso é aceitável, instrução ou skill; se não pode esquecer, hook.

## Como responder quando não é skill

1. Diga qual tipo serve e por quê, em uma ou duas frases.
2. Pergunte se o usuário ainda quer procurar uma skill.
3. Só então busque.

## Estados na coleção de skills

| Estado | Significado | Como tratar |
|---|---|---|
| **candidato** | encontrada, ainda não usada em tarefas reais | não recomende como padrão |
| **adotado** | usada com sucesso em tarefas reais | pode recomendar |
| **compartilhado** | útil para outras pessoas ou repositórios | entra no índice mantido |
| **a retirar** | duplicada, desatualizada ou que não dispara quando deveria | proponha remover |

Promova por **uso observado**, **encaixe claro do gatilho** e **manutenção**, não por novidade.
