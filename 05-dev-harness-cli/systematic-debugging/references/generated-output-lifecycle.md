# Regressões de geração e ciclo de vida da entrega

## 1. Fixe o requisito e reproduza na fronteira

- Compare as asserções existentes com o aceite antes de corrigir: um teste verde pode exigir o comportamento errado.
- Para saída gerada, execute o reconciliador real com dados sintéticos mínimos e uma alegação inédita sem entidades ou números. Schema válido não prova proveniência.
- Para telas, passe erros reais pelo reducer e renderize o consumidor. Cubra limite, validação e falha genérica; fases válidas sem ramo visual podem esconder mensagem e recuperação.

## 2. Corrija o comportamento, não só a fixture

### Proveniência de resumo

Se filtros lexicais aceitarem recombinações inventadas, considere resumo extrativo conservador: exija que cada frase completa normalizada tenha uma fonte admissível do candidato. Exclua vaga, enunciado de pergunta e cargo desejado como evidência de realização. Não remova negações de dentro da frase para torná-la afirmativa. Sem lastro, preserve texto confirmado ou fallback neutro, sem impedir edição/download.

Teste uma frase válida seguida de invenção, palavras conhecidas recombinadas, negativas, fontes não admissíveis e afirmações confirmadas. Documente a perda de paráfrases legítimas: correspondência textual não é garantia semântica e não deve ser vendida como tal.

### Entrega obrigatória e consumo

Valide todas as seções obrigatórias antes de consumir crédito, confirmar transação ou emitir conclusão. Em plano ausente/inválido, teste conjuntamente: erro recuperável, consumo falso, nenhum e-mail de sucesso, liberação de reserva/lease e nova tentativa possível. Cubra modos com mecanismos diferentes de cota. Preserve listas vazias permitidas pelo contrato; não force recomendações inventadas para satisfazer a validação.

### Recuperação e retenção na UI

Mantenha mensagem e retorno ao editor/download para erro de validação e cota esgotada; não ofereça apenas repetir a mesma requisição inválida. Se o reducer for compartilhado, prefira corrigir o consumidor específico antes de alterar as fases de outras jornadas.

Distinga armazenamento da aba, estado React e servidor. Se edição/download exigirem manter dados após concluir, ofereça exclusão explícita e descreva esse ciclo com precisão, inclusive a possibilidade de salvar outro rascunho ao voltar. Não apague dados prematuramente só para tornar verdadeira uma promessa de descarte.

## 3. Verifique a integração

Rode regressões e gates no SHA combinado, não some contagens dos worktrees. Use navegador com dados sintéticos para confirmar mensagem, retorno e descarte; declare fetch interceptado como simulação. Teste CSS print separadamente do download por biblioteca: são mecanismos distintos. Para geometria, margens e conteúdo preservado em PDF real, carregue `chromium-print-regression`.
