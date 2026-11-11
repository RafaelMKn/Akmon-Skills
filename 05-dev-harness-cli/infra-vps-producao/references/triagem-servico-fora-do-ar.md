# Triagem de serviço "fora do ar" — de fora para dentro

Objetivo: separar **máquina caída** de **proxy vivo com upstream morto** e descobrir o caminho de
acesso, antes de pedir qualquer coisa ao usuário. Tudo aqui é read-only.

## 1. Achar os hostnames

O pedido costuma dizer "a VPS do cliente X". O README do cliente lista as instâncias/URLs, mas não
necessariamente o IP. Use os hostnames do README e resolva cada um com `dig +short A`. Hosts no
mesmo IP estão na mesma máquina.

## 2. Testar cada host e ler o sinal

```bash
for h in <hosts>; do dig +short A $h; curl -sS -o /dev/null -m 15 \
  -w "$h HTTP %{http_code} ip=%{remote_ip} t=%{time_total}s\n" https://$h/; done
curl -sS -m 15 -D - -o /dev/null https://<host>/ | head   # header server: nginx/traefik
echo | openssl s_client -connect <ip>:443 -servername <host> 2>/dev/null | openssl x509 -noout -subject -dates
nc -zvw5 <ip> 22
```

| Sinal | Leitura |
|---|---|
| Timeout/conexão recusada em todos os hosts do IP | máquina, rede ou firewall |
| **502 rápido** (< 1s) num host, outros hosts do mesmo IP 200 | proxy vivo, **upstream daquele host morto** (container parado, crash loop, porta mudou) |
| 504 depois de esperar | upstream vivo mas travado/lento |
| Cert `TRAEFIK DEFAULT CERT` | nenhum router casou (ver `traefik-hostnames-tls.md`) |
| Cert certo e válido + porta 22 aberta | a máquina está de pé; o problema é interno |

Teste também um path de webhook (`/webhook/x` no n8n): se ele dá 502, **tráfego de produção está
sendo perdido agora** — diga isso no relato, é o impacto de negócio.

## 3. Tentar acesso antes de concluir

- SSH: `ssh -i <chave> -o BatchMode=yes -o ConnectTimeout=10 root@<ip> 'uptime; df -h /; free -m; docker ps -a'`.
  Estar em `known_hosts` não prova que a chave está instalada: `Permission denied` é a resposta.
  Sem bloco no `~/.ssh/config`, teste as chaves de `~/.ssh/` contra o IP resolvido do hostname.
- API do provedor: rode `LIST_VIRTUAL_MACHINES` em **todas** as conexões do toolkit (Composio) e
  procure o IP. Se não aparece, `whois <ip>` mostra o provedor — a VM está na conta do cliente,
  não na sua.

## 4. Painel de sites (CloudPanel e similares) não é acesso root

Quando o usuário oferece um painel de sites, confira se o hostname quebrado está na lista. Se o
nginx atende o host (cert emitido para ele) mas ele **não aparece no painel**, o serviço foi
montado por fora: container Docker + vhost nginx manual. O painel não enxerga nem reinicia esse
container, e os usuários de site são restritos. O que destrava é root, pelo console web da VM no
painel do **provedor** (hPanel etc.), instalando a chave pública em `authorized_keys`.

Ofereça sempre duas saídas: instalar a chave (você diagnostica) ou o usuário rodar um bloco curto
no console e colar a saída:

```bash
docker ps -a --format '{{.Names}}\t{{.Status}}'; df -h /; free -m
grep -rl "<host>" /etc/nginx/ 2>/dev/null
```

## 5. Container não resolve vizinho (`EAI_AGAIN <nome-do-container>`)

Sintoma no n8n: nó Redis/HTTP falha com `getaddrinfo EAI_AGAIN <container>` enquanto o container
alvo está `Up` há semanas. É rede Docker, não o serviço alvo. Diagnóstico read-only, em uma chamada:

```bash
# redes, início e restarts de cada lado
for c in <app> <alvo>; do echo "$c: $(docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}| started {{.State.StartedAt}} | restarts {{.RestartCount}}' $c)"; done
# quem está em cada rede do alvo
for n in <redes do alvo>; do docker network inspect -f '{{range .Containers}}{{.Name}} {{end}}' $n; done
# o compose declara a rede compartilhada? (redija segredos)
grep -n -i network /docker/<projeto>/docker-compose.yml*; ls -la --time-style=full-iso /docker/<projeto>/
# linha do tempo: recriação, connect/disconnect (sem a rede bridge, que é ruído de exec)
docker events --since <ini> --until "$(date -u +%Y-%m-%dT%H:%M:%S)" --filter type=network \
  --format '{{.Time}} {{.Action}} {{.Actor.Attributes.name}} {{.Actor.Attributes.container}}' | grep -v ' bridge '
# ligação manual anterior e janela real do erro
grep -n 'network connect' /root/.bash_history
docker logs --since <ini> --timestamps <app> 2>&1 | grep GetAddrInfoReqWrap | cut -c1-13 | sort | uniq -c
```

Leitura: container do app **iniciado depois** do último evento de connect manual + compose sem a
rede compartilhada + `connect` manual no `.bash_history` = a recriação apagou a ligação. A hora do
1º/último erro vem dos **logs do container**, não da amostra de execuções da API do n8n (limitada
às N mais recentes). Um `network connect` recente nos eventos mostra que alguém já religou à mão —
atenue o incidente, mas registre que a correção permanente (rede `external: true` no compose) falta.

Imagem do n8n não tem `getent` nem `sqlite3` no Node; teste DNS com
`docker exec <app> nslookup <alvo>`. `docker events --format` com comando multilinha de `exec`
quebra laço `while read`: filtre `--filter type=network` antes de formatar datas.

## 6. Monitor que não avisou é achado

Se a queda não foi detectada, veja quando o monitor (health check) rodou pela última vez.
Monitor parado é pendência própria no relato.
