# Avaliar ferramenta de terceiro antes de adotá-la num projeto de cliente

Use antes de rodada que decide adotar/trocar runtime, cockpit, SaaS ou app open source. Cada achado entra em "Fatos verificados" com URL e data; o que não foi lido fica VERIFICAR.

## Feature anunciada ("a ferramenta X lançou Y")

- Confirme no changelog primário, não em post: `gh api 'repos/<owner>/<repo>/releases?per_page=40'` e filtre o `body` por palavra-chave; abra o PR com `gh pr view <n> -R <owner>/<repo> --json title,body,mergedAt`.
- Registre data do release e maturidade (dias de uso, como foi testada, superfícies sem suporte). Feature lançada no mesmo dia empata no papel, não em operação.
- Leia o doc de arquitetura do repo (`docs/architecture/*.md`) para os modos e o padrão (ex.: automático × perguntar × desligado). O padrão costuma ser o mais agressivo.

## Licença e uso comercial

- Leia `LICENSE` do repo (`gh api repos/<o>/<r>/contents/LICENSE --jq .content | base64 -d`); `license` NOASSERTION na API = licença customizada ou não-SPDX, leia o arquivo.
- Source-available ≠ open source: PolyForm Noncommercial, BSL, SSPL etc. Procure a página de licença comercial e a definição de "Commercial Use": trabalho para clientes e hospedagem para terceiros costumam estar dentro.
- Separe **trava técnica** (o software checa licença?) de **impedimento contratual**. Ausência de trava não autoriza uso; diga isso ao usuário com o mecanismo do risco.
- "Grátis até <data>" na página de preços pode ser trial da licença paga (contrata com cartão, cobra na data). Confira no doc de billing/arquitetura. Divergência entre página de preços e Termos (ex.: mínimo de assentos) fica VERIFICAR.
- Versões antigas podem ter licença permissiva; confira se têm a feature que motivou a troca.

## Operação no ambiente do cliente

- Existe modo headless/self-host (imagem Docker oficial, CLI de servidor)? Exige conta/login no serviço do fornecedor mesmo self-hosted?
- Privacidade: onde ficam conversas e anexos, o que passa por relay do fornecedor, se app de celular guarda cópia local. Confronte com a regra de dados do projeto (pseudônimos, LGPD).
- Agendamento da ferramenta é determinístico ou cada disparo é um turno de LLM (limite por hora, cota, modo de execução irrestrito)? Componente que protege dinheiro ou dado não deve depender de turno de LLM.
- Ritmo de releases e se dá para fixar versão / desligar auto-update.

## Integração com o runtime que já existe

- Quando a ferramenta inicia outro agente como provider (ex.: `hermes acp`), leia a seção do provider: qual diretório de config ela usa, o que sobrepõe ou trava, se pode reescrever o config. Recomende perfil/home separado do usado em produção.
- Dois mecanismos de aprendizado/escrita de skill no mesmo perfil disputam escrita: deixe um só ligado, com portão de aprovação.
