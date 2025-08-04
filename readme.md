# Ferramenta de Correção de Texto

**Correção de texto alimentada por IA com suporte a atalhos globais**

Uma aplicação desktop profissional que fornece correção de texto em tempo real usando a IA Gemini do Google, com atalhos personalizáveis e integração com a bandeja do sistema.

## Funcionalidades

- **Ativação por Atalho Global** - Acione a correção de texto de qualquer lugar com atalhos personalizáveis
- **Correção Alimentada por IA** - Utiliza o Google Gemini para correção inteligente de texto
- **Integração com Área de Transferência** - Funciona perfeitamente com a área de transferência do sistema
- **Notificações Desktop** - Notificações elegantes para atualizações de status
- **Integração com Bandeja do Sistema** - Executa silenciosamente em segundo plano
- **Suporte Multi-idioma** - Prompts em português e inglês
- **Interface Moderna** - Interface limpa e profissional
- **Configurações Persistentes** - Configurações salvas com interface fácil de usar

## Arquitetura

Este projeto implementa os princípios de **Arquitetura Limpa** com clara separação de responsabilidades:

```
text_correction_tool/
├── domain/           # Lógica de negócio e modelos
├── application/      # Casos de uso e orquestração  
├── infrastructure/   # Serviços externos e dados
├── presentation/     # Componentes de UI e integração do sistema
└── main.py           # Raiz de composição da aplicação
```

### Camadas da Arquitetura

- **Camada de Domínio**: Lógica de negócio central, modelos e serviços
- **Camada de Aplicação**: Casos de uso que orquestram serviços de domínio
- **Camada de Infraestrutura**: Integrações de API externas, repositórios, serviços técnicos
- **Camada de Apresentação**: Componentes de UI, bandeja do sistema, gerenciamento de atalhos

## Início Rápido

### Pré-requisitos

- Python 3.8 ou superior
- Chave da API do Google Gemini

### Instalação

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seuusuario/text-correction-tool.git
   cd text-correction-tool
   ```

2. **Crie um ambiente virtual** (recomendado)
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure a chave da API**
   
   Edite `config.py` e adicione sua chave da API Gemini:
   ```python
   GEMINI_API_KEY = "sua_chave_api_gemini_aqui"
   ```

5. **Execute a aplicação**
   ```bash
   python main.py
   ```

## Como Usar

1. **Inicie a aplicação** - O app executará na bandeja do sistema
2. **Copie o texto** - Copie qualquer texto que precisa de correção para a área de transferência
3. **Pressione o atalho** - Use `Alt+S` (padrão) para acionar a correção
4. **Obtenha os resultados** - O texto corrigido é automaticamente colado (se habilitado)

### Configuração das Definições

Clique com o botão direito no ícone da bandeja do sistema e selecione "Configurações" para configurar:

- **Atalho**: Altere a tecla de atalho global
- **Colar automático**: Ative/desative a colagem automática do texto corrigido
- **Notificações**: Habilite/desabilite notificações desktop  
- **Idioma**: Escolha o idioma dos prompts de correção

## Dependências

- **google-generativeai**: Integração com IA Gemini do Google
- **pynput**: Detecção de atalhos globais
- **pyperclip**: Operações de área de transferência
- **pystray**: Integração com bandeja do sistema
- **Pillow**: Processamento de imagem para ícone da bandeja
- **tkinter**: Framework de GUI (incluído com Python)

## Desenvolvimento

### Estrutura do Projeto

```
text_correction_tool/
├── domain/
│   ├── models.py          # Modelos de domínio (CorrectionRequest, AppSettings, etc.)
│   └── services.py        # Lógica de negócio (TextCorrectionService)
├── application/
│   └── use_cases.py       # Casos de uso da aplicação
├── infrastructure/
│   ├── ai_providers.py    # Implementações de serviços de IA
│   ├── repositories.py    # Persistência de dados
│   └── services.py        # Serviços técnicos
├── presentation/
│   ├── ui_components.py   # Componentes de UI e notificações
│   └── system_integration.py # Bandeja do sistema e atalhos
├── main.py               # Ponto de entrada da aplicação
├── config.py            # Configurações
├── requirements.txt     # Dependências
└── README.md           # Este arquivo
```

### Princípios de Design

- **Princípios SOLID**: Responsabilidade única, aberto/fechado, inversão de dependência
- **Arquitetura Limpa**: Separação de responsabilidades entre camadas
- **Injeção de Dependência**: DI manual na raiz de composição
- **Design Baseado em Protocolo**: Interfaces abstratas para melhor testabilidade
- **Tratamento de Erros**: Logging abrangente e degradação graciosa

### Componentes Principais

- **TextCorrectionService**: Lógica de negócio central para correção de texto
- **GeminiAIProvider**: Integração com API do Google Gemini
- **NotificationService**: Gerenciamento de notificações desktop
- **HotkeyListener**: Detecção de atalhos de teclado globais
- **SettingsRepository**: Armazenamento persistente de configuração

## Configuração

### Configurações Padrão

```python
DEFAULT_SETTINGS = {
    "hotkey": "alt+s",
    "auto_paste": True,
    "show_notifications": True,
    "prompt_language": "Portuguese",
}
```

### Variáveis de Ambiente

Você também pode configurar a chave da API via variável de ambiente:

```bash
export GEMINI_API_KEY="sua_chave_api_aqui"
```

## Solução de Problemas

### Problemas Comuns

1. **Atalho não funciona**
   - Verifique se outra aplicação está usando o mesmo atalho
   - Tente executar como administrador (Windows)
   - Verifique o formato do atalho (ex: 'alt+s', 'ctrl+shift+c')

2. **Erros de API**
   - Verifique se sua chave da API Gemini está correta
   - Verifique a conexão com a internet
   - Certifique-se de que as cotas da API não foram excedidas

3. **Ícone da bandeja do sistema não aparece**
   - Verifique se a bandeja do sistema está habilitada no seu SO
   - Tente reiniciar a aplicação
   - Verifique se todas as dependências estão instaladas

### Logs

Os logs da aplicação são salvos em `text_correction.log` no diretório da aplicação.

## Instalação no Arch Linux

### Método Recomendado - Ambiente Virtual

```bash
# 1. Navegar para o diretório do projeto
cd text_correction_tool

# 2. Criar ambiente virtual
python -m venv venv

# 3. Ativar ambiente virtual
source venv/bin/activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Executar aplicação
python main.py
```

### Uso Diário no Arch

```bash
# Sempre ativar o ambiente antes de usar
source venv/bin/activate
python main.py

# Desativar quando terminar
deactivate
```

### Script de Configuração Automatizada

```bash
#!/bin/bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Configuração concluída! Execute: source venv/bin/activate && python main.py"
```

## Contribuindo

1. Faça um fork do repositório
2. Crie uma branch de funcionalidade (`git checkout -b feature/funcionalidade-incrivel`)
3. Commit suas mudanças (`git commit -m 'Adiciona funcionalidade incrível'`)
4. Push para a branch (`git push origin feature/funcionalidade-incrivel`)
5. Abra um Pull Request

### Diretrizes de Contribuição

- Siga os princípios de Clean Architecture
- Mantenha a cobertura de testes
- Use type hints em todo código novo
- Documente novas funcionalidades
- Siga os padrões de código existentes

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Agradecimentos

- **Google Gemini AI** pelas poderosas capacidades de geração de texto
- **Comunidade Python** pelas excelentes bibliotecas e frameworks
- **Princípios de Arquitetura Limpa** de Robert C. Martin
- **Comunidade Open Source** por inspiração e boas práticas

## Estatísticas do Projeto

- **Linhas de código**: ~2.500
- **Arquivos**: 12
- **Camadas de arquitetura**: 4
- **Padrões de design implementados**: 8+
- **Dependências externas**: 5

## Roadmap

### Versão 2.1
- [ ] Suporte a mais idiomas (Espanhol, Francês)
- [ ] Cache inteligente de correções
- [ ] Métricas de uso e estatísticas
- [ ] Temas personalizáveis

### Versão 2.2
- [ ] Integração com outros provedores de IA
- [ ] Plugin para editores de texto
- [ ] Sincronização na nuvem de configurações

## Links Úteis

- [Documentação do Google Gemini](https://ai.google.dev/)
- [Clean Architecture em Python](https://clean-architecture-python.readthedocs.io/)
- [Padrões de Design Python](https://python-patterns.guide/)

---

**Feito com ❤️ e princípios de Arquitetura Limpa**

*Aplicação desktop profissional demonstrando práticas modernas de desenvolvimento Python*
