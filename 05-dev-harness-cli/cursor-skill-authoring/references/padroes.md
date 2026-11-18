# Padrões de corpo para skills

Escolha o padrão que combina com o tipo de tarefa. Todos os exemplos abaixo foram escritos para este guia.

## 1. Modelo de saída

Mostre o formato exato esperado.

```markdown
## Relatório
**Resumo:** <uma frase>
**Achados:** lista com severidade (alta, média, baixa)
**Próximo passo:** <ação>
```

## 2. Exemplos de entrada e saída

Dois ou três pares curtos valem mais que uma descrição longa.

```markdown
Entrada: "corrigir bug do login"
Saída (mensagem de commit): fix(login): corrige redirecionamento após sessão expirada
```

## 3. Fluxo com checklist

Para tarefas com etapas que não podem ser puladas.

```markdown
- [ ] Ler o arquivo de configuração
- [ ] Rodar a validação
- [ ] Aplicar a alteração
- [ ] Rodar a validação de novo
```

## 4. Fluxo condicional

Ramifique por tipo de tarefa.

```markdown
- Criando documento novo → siga "Criação".
- Editando documento existente → siga "Edição".
```

## 5. Ciclo de validação

Execute o validador, corrija, repita até passar. Informe ao usuário se não passou.

## Escolhendo

- Saída tem formato rígido → modelo de saída.
- Qualidade depende de estilo → exemplos.
- Erro custa caro se uma etapa for pulada → checklist.
- Há bifurcações claras → fluxo condicional.
- Existe um verificador automático → ciclo de validação.
