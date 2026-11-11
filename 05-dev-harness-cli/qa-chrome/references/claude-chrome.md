# Claude in Chrome — procedimento de envio e acompanhamento

STATUS: procedimento NÃO validado ao vivo. Nenhum envio real foi exercitado quando esta skill foi escrita. Trate cada passo como hipótese a verificar e registre o que realmente ocorreu. Não existem endpoints, seletores ou atalhos garantidos aqui; descubra-os no momento.

## Estado do ambiente: sempre reverificar
- Presença em disco NÃO prova: extensão habilitada, versão ativa, login, plano com acesso, permissões concedidas nem entrega do prompt.
- A cada execução: `computer_use(action="list_apps")` e `list_windows`; Chrome rodando? Perfil certo (`Default` ou outro)? Pergunte ao usuário se houver mais de um perfil/janela.
- Chrome fechado: abrir no perfil identificado para cumprir o envio faz parte da execução solicitada. Descobrir o comando real instalado; não instalar, relançar com flags inseguras nem alterar configuração. Se houver risco de interromper trabalho ou não for possível identificar o perfil correto, perguntar; se não puder abrir, registrar bloqueio e entregar fallback manual.

## Passos
1. Carregar a skill `computer-use` e ler o schema vivo da tool `computer_use` (ações aceitas, `delivery_mode`, `capture`). Use só ações que o schema listar.
2. `capture` com `mode="som"` e `app` do Chrome. Procurar na árvore/captura: botão da extensão na barra, painel lateral ou popup da extensão Claude. Se o painel não estiver aberto, abri-lo é interação com chrome do navegador (barra de extensões); fazer por elemento indexado, verificando com nova captura. Não inventar atalhos: se precisar de um, confirmar o texto no menu/tooltip da própria UI.
3. Verificar sinais de bloqueio ANTES de digitar: tela de login, 2FA, aviso de plano/permissão, pedido de permissão de site. Qualquer um: parar e ir a "Intervenção". Não digitar credenciais nem aceitar permissões sensíveis em nome do usuário.
4. Conferir alvo, SHA, URL do painel e perfil com a solicitação da execução. O envio automático faz parte do contrato Q6/Q9: não exigir outra confirmação quando o alvo já estiver inequívoco. Perguntar somente diante de ambiguidade de perfil/alvo ou efeito sensível não autorizado.
5. Enviar o prompt integral de `prompt-claude-chrome.md`: focar o campo de entrada pelo índice, `type` (ou `set_value` se o schema oferecer e o campo aceitar), re-capturar e comparar o início e o fim do texto colado. Prompts longos podem ser truncados ou ter quebras de linha submetidas cedo; se a captura mostrar divergência, não enviar; ir ao fallback.
6. Acionar o envio (botão de enviar por índice). Seguir a escada verify→escalate da skill `computer-use`: `confirmed`/`unverifiable` exige captura nova; só subir de rung diante de sinal retornado.
7. Confirmar início: a captura deve mostrar a mensagem enviada na conversa e a extensão trabalhando (resposta em curso). Só então registrar "enviado e iniciado". Efeito incerto: reler a conversa, nunca reenviar às cegas.
8. Acompanhar em ciclos limitados: `wait` curto, `capture`, ler progresso e pedidos de intervenção. Limite de ciclos combinado (padrão 10); ao esgotar, parar, gravar estado e dizer como retomar. Sem espera indefinida.
9. Ler o resultado: extrair da conversa os blocos por cenário (ID, resultado, observado, evidência, intervenção). O que o Hermes não consegue ver ou reproduzir permanece "relato não verificado".

## Intervenção do usuário
Dizer: item afetado, impedimento, ação exata (ex.: fazer login na extensão), como retomar (run-dir + ID do cenário). Continuar cenários independentes quando possível.

## Fallback manual
Disparar quando: Chrome/extensão ausente, login/2FA/permissão, GUI sem efeito após a escada, campo truncando, ou captura impossível (Wayland/DISPLAY: `hermes computer-use doctor`). Entregar o caminho de `prompt-claude-chrome.md` e `checklist.md`, instruções de colar e como trazer a resposta de volta. Não afirmar envio.

## O que registrar do envio
Janela/perfil usados, horário, captura/descrição que prova recebimento, ciclos de acompanhamento, e se houve fallback.

## Limites desta referência
Sem teste ao vivo: UI da extensão, nomes de botões e se `type` entrega o prompt longo são desconhecidos. A primeira execução real deve atualizar este arquivo com o que foi observado (sem segredos).
