# Registro de pastas: `skills.json` e `plugins.json`

> ⚠️ Verificar na doc oficial: nenhuma das páginas públicas consultadas descreve estes dois arquivos. Todo o conteúdo abaixo vem da especificação funcional interna. Antes de gravar para o usuário, confirme o formato em `https://antigravity.google/docs` e avise que não foi confirmado.

Os dois arquivos têm o mesmo formato e servem para carregar itens que estão fora das pastas padrão.

## Campos

- `entries`: lista de objetos:
  - `path` (obrigatório): pasta a carregar.
  - `include_only`: lista de regex aplicada ao **nome da pasta**; se existir, só carrega o que casar.
  - `exclude`: lista de regex; o que casar é ignorado.
- `inherits`: lista de arquivos JSON do mesmo tipo (mesmos campos), processados na ordem listada.

## Resolução de `path`

| Começa com | Significa |
|---|---|
| `/` | caminho absoluto |
| `~/` | relativo à home do usuário |
| qualquer outro | relativo à raiz do repositório |

## Exemplo para equipe

Estrutura versionada:

```
equipe-skills/
  revisao-de-pr/SKILL.md
  release-notes/SKILL.md
.agents/skills.json
```

```json
{
  "entries": [
    { "path": "equipe-skills", "exclude": ["^rascunho-"] }
  ]
}
```

Assim quem clonar o repositório carrega as skills da equipe sem copiar nada para a máquina.

## Cuidados

- Valide o JSON antes de gravar.
- Se o `path` não existir, informe e não grave.
