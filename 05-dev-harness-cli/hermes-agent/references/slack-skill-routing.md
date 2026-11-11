# Skills como comandos no Slack

- Diferencie comandos dinâmicos de skills no Hermes de slash nativo do app Slack. Instalar uma skill não registra slash no manifesto, e Slack bloqueia slash nativo em threads.
- Verifique `_rewrite_known_bang_command` e `is_gateway_known_command` no checkout instalado: o normalizador de bang pode aceitar apenas built-ins/plugins, não skills nem quick_commands. Documentação geral não prova !nome-de-skill.
- Para encaminhar texto a uma skill sem editar core, use plugin externo `pre_gateway_dispatch` que retorna `{action: rewrite, text: /skill}`. Não use register_command para isso: handler responde diretamente e pode encerrar dispatch em vez de executar skill.
- Restrinja origem por chat/usuário/workspace e proveniência bruta, preservando autorização downstream. No Slack chat_type=dm pode incluir mpim; exigir channel_type=im quando a privacidade depender de DM individual.
- Antes de exigir restart, confira `hermes plugins enable` e o resultado de `activate_plugin_now`: hooks gateway podem ativar ao vivo pelo control socket. `gateway_reloaded=true`, hook em activated_now.gateway_transforms e restart_required=false são evidência de registro no runtime; não prova de invocação Slack end-to-end.
- Não contorne proteção que impede restart de dentro do gateway. Se recarga suportada não servir, peça restart em shell externo.
- Use `hermes --print-runtime-command` para descobrir o interpretador/bootstrap real. O launcher isolado pode ignorar PYTHONPATH e mudar semântica de --run-module; testes que dependem de pacotes Hermes devem usar runtime real, não python genérico sem dependências.
