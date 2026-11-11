# Leitura de fontes antes de escrever

Use quando a spec, o glossário ou uma decisão depende de documento, nota de reunião ou busca web.

## Docx (propostas, atas, notas de reunião)

Extração sem dependência externa (testada: saída de 15k a 58k caracteres por arquivo):

```python
import zipfile, re, html
x = zipfile.ZipFile(path).read('word/document.xml').decode('utf8')
x = re.sub(r'</w:p>', '\n', x)
x = re.sub(r'</w:tc>', ' | ', x)
x = re.sub(r'<[^>]+>', '', x)
print(html.unescape(x))
```

- Grave a saída em arquivo no scratch e leia em trechos. Tabelas viram linhas com ` | `.
- Controle de alterações (`w:ins` / `w:del`): o texto excluído também aparece no resultado. Verifique com `grep -c '<w:del ' word/document.xml` antes de citar um trecho.
- Comentários (`word/comments.xml`), cabeçalhos e rodapés não entram neste extrator. Se existirem e importarem, leia-os à parte.

## Leitura por trechos

Se a ferramenta de leitura devolver só metadado ("read ... (N chars)" sem o conteúdo), o texto não está no seu contexto. Releia com `offset`/`limit` de 300 a 400 linhas, ou use `sed -n 'A,Bp'` no terminal. Confirme que leu o conteúdo citando uma linha específica antes de usá-lo.

## Resultado de busca web

Resultado que mostra só o tamanho ("(8,669 chars result)") sem trechos não tem conteúdo utilizável. Reformule com consulta mais estreita, ou abra a URL oficial com `web_extract`. Agregador e artigo de terceiro servem para orientar a busca, não para número de limite, plano, prazo ou versão de API: esses vêm da documentação oficial.

## Notas de reunião geradas automaticamente

Atribua a um participante só a fala que está na transcrição. Resumo automático é fonte secundária: cada decisão atribuída a alguém vira "a confirmar" até o próprio usuário confirmar.
