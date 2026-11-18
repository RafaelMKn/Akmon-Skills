---
name: skill-scout
description: "Procura, instala e gerencia skills de agente: pesquisa num índice local de fontes e, sob demanda, no GitHub e na web, e antes disso avalia se o pedido precisa mesmo de uma skill ou de outro tipo de customização (prompt, instrução, agente ou hook); use quando o usuário quiser achar, instalar, favoritar, atualizar ou listar skills, ou perguntar se deve usar skill, prompt, instrução, agente ou hook."
license: MIT
metadata: { author: "Akmon contributors" }
---

# Skill Scout

Acha, instala e organiza skills de agente. O trabalho pesado fica no script `scripts/search_skills.py` (Python 3.10+, só biblioteca padrão). Você conduz a conversa e **traz as decisões ao usuário**.

## Quando usar

- "Existe uma skill para...?", "procure uma skill de..."
- Instalar, favoritar, atualizar o índice, listar skills.
- "Isso deveria ser skill, prompt, instrução, agente ou hook?"

## Pré-condições

- `references/skill-index.json` presente e válido (o script valida contra o esquema; um índice novo vem **vazio**: veja "Índice").
- Para busca de código e atualização do índice: GitHub CLI `gh` 2.0+ autenticado. Sem `gh`, o script usa a API pública sem token, com limite baixo de requisições.
- Python 3.10 ou superior. Detalhes e solução de problemas em `references/setup-guide.md`.

## Passo a passo

1. **Porta de decisão.** Classifique o pedido pela tabela de `references/customization-routing.md`. Se a resposta **não** for skill, explique a alternativa **antes** de buscar e só continue se o usuário ainda quiser uma skill.
2. **Frescor do índice.** O script avisa se o índice tem mais de 7 dias. Pergunte ao usuário se quer atualizar (use a interface do agente, não entrada interativa de terminal; passe sempre `--no-interactive`).
3. **Buscar no índice:** `python3 scripts/search_skills.py "<termos>" --no-interactive`. Termos procuram em nome e descrição (sem diferenciar maiúsculas; todos devem aparecer); `#categoria` filtra por categoria; `--category` e `--source` também filtram. Favoritos vêm primeiro, depois ordem alfabética.
4. **Busca externa**, se o usuário pedir: `--external` (GitHub, arquivos `SKILL.md`; sem resultado, lista repositórios relacionados e sugere `--add-source`). **Busca web:** `--web` mostra links para Google, Bing e DuckDuckGo.
5. **Responder** com: contagem de repositórios e skills pesquisadas, data do índice, tabela (skill, descrição, fonte, confiança) e um bloco numerado de próximos passos. Com **3 ou mais** resultados, recomende uma e dê o motivo. Critérios, em ordem: fonte oficial, riqueza de recursos, relevância para o objetivo, atualização recente. (O índice não traz riqueza nem data de atualização por skill: diga isso se esses critérios decidirem.)
6. **Instalar** (veja a seção abaixo): só com aprovação explícita.
7. **Gestão** (favoritos, similares, fontes, estatísticas): veja "Comandos".

## Instalação: aprovação obrigatória

1. Rode `--install <skill> --no-interactive` **sem** `--approve`. O script só mostra o plano: URL de origem, host, confiança da fonte e as ferramentas/permissões que o `SKILL.md` declara (`allowed-tools`), e termina com código 3.
2. **Mostre isso ao usuário e espere um "sim" explícito.** Hosts aceitos por padrão: `github.com`, `raw.githubusercontent.com`, `gist.github.com`. Outro host exige aprovação específica para a sessão (`--allow-host`).
3. Com a aprovação, repita o comando acrescentando `--approve` (e `--install-dir DIR` se o usuário escolheu um destino; padrão `~/.skills`).
4. O script baixa só arquivos e pastas (sem links simbólicos), grava sem bit de execução, **nunca executa nada baixado** e **nunca sobrescreve** uma pasta existente.
5. Confirme o caminho final ao usuário. Fontes da comunidade: avise que o uso é por conta e risco e sugira ler o `SKILL.md` antes de usar.

## Comandos

| Objetivo | Comando (sempre com `--no-interactive`) |
|---|---|
| Buscar | `search_skills.py "termos"` / `"#categoria"` / `-c cat` / `-s fonte` |
| Detalhes | `--info <skill>` |
| Instalar | `--install <skill> [--install-dir DIR] [--approve]` |
| Similares | `--similar <skill>` (até 5, por categorias em comum; se o nome não existe, por semelhança de caracteres) |
| Favoritos | `--star <skill>`, `--unstar <skill>`, `--list-starred` (chave `fonte/nome`) |
| Listas | `--list-categories`, `--list-sources`, `--stats` |
| Atualizar índice | `--update` |
| Nova fonte | `--add-source https://github.com/dono/repo` (cria a entrada e sincroniza) |
| Ambiente | `--check` (python e `gh`) |
| Saída em JSON | `--json` (junto da busca) |

O nome de uma skill pode ser `nome` ou `fonte/nome` (necessário se houver homônimos em fontes diferentes).

## Índice

O índice distribuído com esta skill começa **vazio, porque cada pessoa monta o seu**. Para populá-lo: `--add-source <url do repositório>` para cada repositório de skills que o usuário queira acompanhar (por exemplo, o do próprio projeto) e depois `--update`. A atualização descobre as pastas com `SKILL.md` em três tentativas, nesta ordem: busca de código do GitHub no repositório; pasta `skills/`; subpastas da raiz. Descrições vêm do `description` do frontmatter (reserva: primeira linha útil do `README.md`), cortadas em 100 caracteres. Entradas novas entram na categoria `geral`; categorias podem ser editadas à mão em `references/skill-index.json`. **Antes de adicionar fontes de terceiros, confirme a licença** e informe o usuário: o índice guarda metadados desses projetos.

Falha numa fonte não interrompe as outras: o script lista as falhas ao final.

## Coleção do usuário

Classifique cada candidato como **candidato**, **adotado**, **compartilhado** ou **a retirar** (definições em `references/customization-routing.md`). Não promova por novidade: promova por uso observado, encaixe claro do gatilho e manutenção.

## Comunicação

- Não mostre comandos ao usuário; execute internamente (depois da aprovação, quando exigida) e relate o resultado.
- Responda só com skills presentes no índice ou em resultados verificados. Nunca invente skills.
- Regras detalhadas e checklist: `references/agent-instructions.md`.

## Arquivos

- `scripts/search_skills.py`: ferramenta principal. `scripts/test_search_skills.py`: testes offline (`python3 scripts/test_search_skills.py`).
- `references/skill-index.json`, `skill-index.schema.json`, `starred-skills.json`: dados e esquema.
- `references/customization-routing.md`, `agent-instructions.md`, `setup-guide.md`.
