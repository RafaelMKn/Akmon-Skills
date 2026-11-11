# Podman: broken pipe ao receber TAR por stdin

- Isole `podman cp - contêiner:/destino` em contêiner próprio, `--network none --pull never --entrypoint sleep`, usando texto sintético; nunca reproduza com segredos ou iniciando uma stack de banco inteira.
- Compare cópia por caminho local, TAR por stdin com contêiner parado, e o mesmo TAR com apenas `sleep` iniciado; os caminhos internos de extração diferem.
- Varie somente o padding TAR: GNU tar padrão pode produzir 10.240 bytes para arquivo mínimo; `tar --blocking-factor=1 -cf - ...` produz o TAR mínimo com os blocos de fim válidos. Não remova zeros finais cegamente: zeros podem pertencer ao conteúdo ou ao padding obrigatório do último membro.
- Faça readback do arquivo mesmo após `passing bulk input to subprocess: write |1: broken pipe`: o conteúdo pode ter sido extraído antes de o copiador falhar ao enviar padding ao subprocesso.
- Examine o copiador Buildah vendorizado na versão exata do Podman; `io.Copy(bulkReaderWrite, bulkReader)` pode reportar EPIPE depois de o leitor TAR atingir EOF e o subprocesso encerrar com sucesso. Não conclua falha de permissão ou SELinux apenas pelo texto `broken pipe`.
- Teste `--archive=false` e `podman unshare` só como hipóteses isoladas, não como correções presumidas. No Podman rootless 5.8.7, ambos podem manter a falha com TAR padded.
- Verifique como o chamador gera o TAR: `TAR_OPTIONS` não altera `Bun.Archive`. Um workaround comprovado com GNU tar não prova correção do comando Supabase completo.
- Confirme readback byte a byte e repita RED/GREEN; preserve logs de códigos de saída sem conteúdo sensível.
- Remova somente probes criados na execução e confirme ausência. Confira `Config.Volumes` da imagem antes de criar para não deixar volumes anônimos; nunca remova recursos preexistentes.
