# Consultar schemas e validar pelo MCP stdio

Use quando o harness não expõe as ferramentas n8n-mcp, mas o workspace já tem um launcher configurado. REST recupera o workflow; não substitui descoberta de schema nem validação MCP.

## Procedimento

1. Confirme o alvo pelo projeto e leia o launcher existente antes de executá-lo. No workspace, `tools/run_n8n_mcp.py <PREFIXO>` resolve as credenciais internamente e inicia o n8n-mcp em stdio. Execute a partir da raiz do workspace. Não imprima o ambiente nem passe chave em argumento.
2. Confira a disponibilidade do SDK no mesmo interpretador: `python3 -c 'import mcp; from mcp.client.stdio import stdio_client'`. Use o pacote já disponível; não faça instalação ou atualização de dependências por conveniência sem conferir o ambiente.
3. Inicialize a sessão, liste as ferramentas e consulte o schema real da ferramenta desejada. Os nomes dos campos no SDK Python podem ser snake_case: na interface exercitada, o schema é `tool.input_schema`, embora o protocolo JSON use `inputSchema`. Prefira `tool.model_dump(by_alias=True)` ao inspecionar o envelope completo, em vez de supor o nome do atributo.
4. Consulte `get_node` antes da configuração. Para mudança pontual, valide o export anterior e o payload candidato com as mesmas opções e compare erros e avisos; warning preexistente não justifica refatoração de carona.
5. Vincule os relatórios ao payload exato que será escrito. Mudança no payload exige nova validação. Releitura da versão ativa e prova comportamental continuam sendo etapas separadas.
6. Encerre os context managers para fechar a sessão e o subprocesso. O servidor pode emitir mensagens normais de encerramento em stderr; avalie o retorno da ferramenta e o exit code, não apenas a presença de stderr.

## Receita de consulta e validação

O exemplo recebe prefixo, launcher existente e export JSON; só consulta schemas e valida em memória, sem escrever na instância. Use caminhos absolutos nos argumentos ou execute na raiz do workspace.

```python
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def unpack(result):
    if result.is_error:
        raise RuntimeError('A ferramenta MCP retornou erro; examine a saída em privado.')
    return json.loads(next(item.text for item in result.content if item.type == 'text'))


async def main(prefix, launcher, export_path):
    workflow = json.loads(Path(export_path).read_text(encoding='utf-8'))
    params = StdioServerParameters(command=sys.executable, args=[launcher, prefix])
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            tools = await session.list_tools()
            by_name = {tool.name: tool for tool in tools.tools}
            for name in ('get_node', 'validate_workflow'):
                print(json.dumps(by_name[name].model_dump(by_alias=True), ensure_ascii=False))
            schema = unpack(await session.call_tool('get_node', {
                'nodeType': 'nodes-langchain.agent', 'detail': 'standard',
            }))
            print('nodeType:', schema.get('nodeType'), 'version:', schema.get('version'))
            report = unpack(await session.call_tool('validate_workflow', {
                'workflow': workflow,
                'options': {'profile': 'runtime'},
            }))
            print(json.dumps({
                'valid': report.get('valid'), 'summary': report.get('summary'),
            }, ensure_ascii=False))


if __name__ == '__main__':
    asyncio.run(main(*sys.argv[1:]))
```

O nome e os argumentos acima foram exercitados com o SDK Python e o launcher do workspace. Confirme-os com `list_tools()` se o servidor mudar. Exports e relatórios completos podem conter segredos ou dados pessoais: mantenha-os privados e mostre apenas o resumo necessário. Não transforme este caminho de consulta em mecanismo para criar workflows de leitura de banco ou contornar gates de escrita.
