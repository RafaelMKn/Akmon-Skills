---
name: cursor-cli-statusline
description: "Configura uma linha de status personalizada acima do prompt da CLI do Cursor (statusLine em cli-config.json, com script que lê JSON da sessão); use quando o usuário mencionar status line, statusline, barra de status ou rodapé da CLI, ou quiser mostrar modelo, uso de contexto, branch ou pasta acima do prompt."
license: MIT
metadata: { author: "Akmon contributors" }
---

# Status line da CLI do Cursor

A linha de status é gerada por um **comando seu**. A CLI o executa a cada atualização da conversa, entrega um JSON com dados da sessão pela **entrada padrão** e exibe o texto que ele imprime na **saída padrão**, acima do prompt. Roda localmente e **não consome tokens**.

> O Cursor também tem uma skill embutida `/statusline` que configura isso. Se o usuário a tiver, ela é uma alternativa; esta skill orienta a configuração manual e a depuração.

## Quando usar

Menções a `status line`, `statusline`, `statusLine`, barra de status da CLI, rodapé do prompt, ou o desejo de ver dados da sessão (modelo, contexto, branch, pasta, modo vim) acima do prompt.

## Informações necessárias

- O que mostrar na linha.
- Forma de execução: arquivo de script ou comando inline.
- Pré-condições: `~/.cursor/cli-config.json` existente e com JSON válido (ver `cursor-cli-config`); script executável; ferramenta para ler JSON (por exemplo `jq`) instalada (`command -v jq`).

## Passo a passo

1. Defina o conteúdo da linha com o usuário.
2. Escreva o script: leia **toda** a entrada padrão, extraia os campos, monte o texto e imprima. Trate campos ausentes ou nulos com valor padrão.
3. `chmod +x` no script, se for arquivo.
4. **Teste antes de configurar**, com um JSON montado à mão: `echo '<json>' | ./statusline.sh`. A saída deve ser a esperada e o código de saída `0`.
5. Acrescente a chave `statusLine` ao `~/.cursor/cli-config.json`, **preservando as demais chaves** (leia, altere, valide, grave com indentação de 2 espaços).
6. Avise que a alteração deve ser conferida na CLI; configurações da CLI costumam valer após reiniciá-la.

## Configuração

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.cursor/statusline.sh",
    "padding": 0,
    "updateIntervalMs": 300,
    "timeoutMs": 2000
  }
}
```

| Campo | Regra |
|---|---|
| `type` | obrigatório; `"command"` |
| `command` | obrigatório; caminho de executável ou comando inline; aceita `~` e divisão de argumentos no estilo do shell |
| `padding` | opcional; inteiro; padrão `0`; recuo horizontal em caracteres |
| `updateIntervalMs` | opcional; padrão `300`; mínimo `300` |
| `timeoutMs` | opcional; padrão `2000` |

## Comportamento de execução

- Roda a cada atualização da conversa, respeitando o intervalo mínimo.
- Chegou atualização enquanto o comando roda? O processo em andamento é encerrado e outro começa.
- Estourou o tempo limite? O processo é encerrado.
- Saiu com código diferente de zero e sem saída? O texto anterior permanece.
- Várias linhas de saída viram várias linhas na área; cores ANSI funcionam.
- O processo é iniciado sem shell no Unix (com shell no Windows para `.cmd` e `.bat`).
- Relato da comunidade: configurar um `statusLine` customizado **substitui** o rodapé nativo em vez de somar uma linha.

## Campos do JSON de entrada

| Grupo | Campos |
|---|---|
| Sessão | `session_id`, `session_name` (só se houver nome), `transcript_path`, `render_width_chars`, `cwd`, `autorun`, `version` |
| `model` | `id`, `display_name`, `param_summary` (só com parâmetros não padrão), `max_mode` (só se ativo) |
| `workspace` | `current_dir`, `project_dir`, `added_dirs` |
| `output_style` | `name` (`"default"` ou `"compact"`) |
| `context_window` | `total_input_tokens`, `total_output_tokens` (pode ser nulo), `context_window_size`, `used_percentage` (nulo possível), `remaining_percentage` (nulo possível), `current_usage` (nulo antes da primeira chamada) |
| `vim` | `mode` (`"NORMAL"` ou `"INSERT"`); só com vim ativo |
| `worktree` | `name`, `path`; só dentro de worktree |

Com `jq`, use `//` para valores padrão: `.context_window.used_percentage // 0`. O valor de tokens de entrada em `context_window` é uma estimativa derivada de porcentagem.

Há um script de exemplo em `templates/statusline.sh`.

## Resposta ao usuário

Script criado e executável (se houver), entrada `statusLine` válida sem alterar outras chaves, resultado do teste com JSON de exemplo. Se não foi possível conferir visualmente na CLI, diga isso.

> ⚠️ Verificar na doc oficial: a página de configuração da CLI do Cursor **não documenta** `statusLine`; os campos, padrões (`updateIntervalMs`, `timeoutMs`) e o JSON de entrada acima vêm da especificação interna e de relatos da comunidade. O histórico de versões confirma que a linha de status customizada existe (abril de 2026). Se a CLI rejeitar algum campo, siga o que a skill embutida `/statusline` gerar. Também não está confirmado se a mudança vale na hora ou só após reiniciar.
