# Supabase local: Podman stdin TAR com broken pipe

## Sintoma e diagnóstico
`supabase start` pode falhar com `failed to copy secret file into container` / `passing bulk input to subprocess: write |1: broken pipe` no Podman rootless. Não atribuir a autenticação, SQL ou Edge antes de reproduzir a fronteira.

Caso observado: Podman 5.8.7, pipe de 8192 bytes. TAR padrão de um marcador tinha 10240 bytes e `podman cp - container:/tmp/` retornava 125; o mesmo arquivo com dados e cabeçalhos intactos e apenas dois blocos EOF finais (2048 bytes totais) retornou 0, com leitura do marcador idêntica. Passar o TAR original por arquivo regular em vez de pipe não resolveu.

Referência upstream: https://github.com/podman-container-tools/buildah/issues/6573 — leitura do TAR termina antes de drenar padding, produtor recebe EPIPE. Sintoma semelhante não basta: repetir probe local isolado.

## Solução de compatibilidade restrita
Preferir correção upstream instalada e validada quando disponível; não atualizar/downgrade global automaticamente. Enquanto necessário, usar wrapper `podman` em PATH EXCLUSIVO do processo Supabase: intercepta somente `podman cp - DESTINO_CONTAINER`, valida TAR sem compressão, preserva bytes até fim dos dados de todos os membros e dois blocos nulos EOF, recusa trailer não nulo ou TAR inválido, chama `/usr/bin/podman` real. Todos os outros comandos são repassados por exec. Não imprimir conteúdo, tokens nem chave do arquivo secreto copiado. Não alterar pipe sysctl, SELinux, sockets ou stacks alheias.

Implementação local de referência (confira existência e leia antes de usar):
`<skill_dir>/scripts/podman-tar-compat/bin/podman`
Testes: `.../podman-tar-compat/test_wrapper.py`.
O wrapper não é instalado globalmente. Um shell futuro sem esse PATH não herda a compatibilidade.

## Prova de conclusão
Exigir teste red/green de cp e leitura de volta; testes de preservação de dados nulos, PAX longo, idempotência e recusa de arquivo inválido/trailer. Depois executar Supabase no projeto descartável exato: exit 0, DB/Auth/API saudáveis e migrations aplicadas iguais aos arquivos da branch. Log de startup pode conter chaves locais: arquivo modo600, nunca entregar sem sanitizar. Containers e env não mudam a origem do código: conferir mounts e identidade da cópia.

## Edge Function 503 BOOT_ERROR em stack nova (SELinux)
Sintoma: `{"code":"BOOT_ERROR","message":"Worker failed to boot"}` e no log do edge runtime `failed to bootstrap runtime: failed to determine entrypoint`. Causa observada no Fedora (SELinux Enforcing): cópia das functions com rótulo `user_home_t`; container `container_t` recebe `Permission denied` no bind mount (`podman exec <edge> ls <dir>` prova). Stacks antigas funcionam porque a pasta delas já tinha `container_file_t`.
Correção restrita: `chcon -R -t container_file_t <copia-descartavel>/supabase/functions` (reversível com `restorecon -R`). Não usar `setenforce 0`, não mudar política e não rotular o worktree do repo. Não precisa reiniciar a stack (per_worker). Prova: POST com anon key retorna erro do PRÓPRIO código da função (ex.: 401 `Sessão inválida`), e não 503; e sem `boot error` no log. Gateway 401 `UNAUTHORIZED_NO_AUTH_HEADER` sem header NÃO prova boot.
Check de prontidão: incluir chamada a pelo menos uma Edge Function no aceite da bancada; health de Auth/REST não cobre Edge.

## Escalonamento
Filho não autorizado a diagnosticar infraestrutura deve parar na primeira ocorrência desse erro conhecido e devolver ao pai. Não permitir que uma tarefa de QA vire manutenção de Podman silenciosamente.
