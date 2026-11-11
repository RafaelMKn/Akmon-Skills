# Bancada de backend real (Supabase local) para homologar checklist

Use ao preparar ou auditar stack descartável + massa sintética + painel para testar PR contra banco real. Infra do Podman/SELinux: `podman-tar-padding.md`.

## Ordem de prontidão (o principal confere cada item antes do próximo filho)
1. **Stack:** CLI `start` com exit 0; Auth/REST 200; migrations aplicadas == arquivos da branch (comparar listas em código); RPC/objeto novo do diff presente; cópia das functions idêntica por hash à branch.
2. **Edge boot:** chamar ao menos uma Edge com anon key e exigir erro vindo do PRÓPRIO código da função. Health de Auth/REST não cobre Edge; 401 do gateway sem header não prova boot.
3. **Edge env:** grep `Deno.env.get(` nas funções do escopo + `.env.exemplo` antes de semear. Variável obrigatória ausente (ex.: URL de redirect exigindo `https://`) vira 503 de negócio no meio do teste. Criar `supabase/functions/.env` MÍNIMO na cópia descartável só com nomes não secretos necessários e provedor de IA em modo simulado; o `start` o injeta (reiniciar só essa stack; `stop` sem flags preserva volumes — reconferir massa depois). Nunca copiar `.env` de outra bancada: pode trazer chave real de LLM.
4. **Massa sintética fiel à produção:** derive o estado de cada perfil do CÓDIGO que o produz, não de flags da tabela. Convite pendente = criado pelo fluxo real de convite (`invited_at` preenchido, sem senha, sem login). Desativado = desativação pela Edge real (ban em `auth.users` + login recusado). Flag `pendente` de sincronização ≠ convite. Crie esses perfis chamando as Edge Functions reais com token aal2 real; proibido UPDATE em `auth.*` ou JWT/claims fabricados. Registro mal rotulado não se apaga: renomeie a categoria no manifesto.
5. **E-mail sintético:** domínio `.invalid` (nunca o domínio real do produto) e conferir que o SMTP do Auth aponta para o inbucket/mailpit local antes do primeiro convite.
6. **Credenciais da massa:** senha aleatória por usuário (`crypto.randomBytes`) persistida só no arquivo privado 600; scripts que leem credencial também 600; varrer arquivos sanitizados por senha/token literais e JWT antes de aceitar.
7. **Painel:** confira para qual backend o painel JÁ aberto aponta (`/proc/<pid>/cwd` + `.env.local`) — pode ser porta morta. Suba Vite novo em porta própria passando `VITE_*` no env do PROCESSO (prioridade sobre `.env.local`), sem editar arquivo do worktree; prove pelo tráfego de rede que vai à API certa.
8. **Playwright fora do repo:** pasta própria com `playwright.config.ts` e symlink `node_modules` -> worktree, rodando o bin do worktree; worktree segue `git status` limpo. Headed exige `DISPLAY` (XWayland serve).

## Fan-out de cenários
- Filhos paralelos só com isolamento por TENANT: um usa só a Empresa A (navegador), outro só a B (banco/HTTP). Mesmo gerente em dois filhos colide em código TOTP/sessão e em renomeações.
- Cross-tenant que DEVE falhar pode usar a outra empresa como vítima, com SELECT provando que nada mudou.
- RPC/guards com JWT de login real (aal1 senha, aal2 senha+TOTP); sonda SQL com `request.jwt.claims` só como complementar.
- Constraint/catálogo via SQL dentro de `BEGIN … ROLLBACK`.
- Mutação de teste restaura o estado pelo fluxo real no fim e lista o estado final.
- Falha do produto é REPROVADO e segue; não é bloqueio.
