# Configuração de Qualidade de Código e Formatação

Este projeto usa formatação de código automatizada e verificações de qualidade que executam antes de cada commit.

## Ferramentas Utilizadas

### 🎨 **Black** - Formatador de Código
- Formata automaticamente código Python para estilo consistente
- Comprimento de linha: 88 caracteres
- Executa a cada commit

### 🔧 **isort** - Organizador de Imports  
- Ordena e organiza automaticamente imports
- Compatível com formatação Black

### 📏 **Flake8** - Linter
- Verifica problemas de qualidade e estilo de código
- Força conformidade com PEP 8
- Compatível com Black (ignora E203, W503)

### 🔍 **mypy** - Verificador de Tipo Estático
- Realiza análise de tipo estático em código Python
- Captura erros relacionados a tipos antes da execução
- Garante que anotações de tipo estejam corretas e consistentes
- Configurado com opções de verificação de tipo estrita

### ✅ **Hooks de Pre-commit**
- Executa automaticamente antes dos commits git
- Previne commit de código mal formatado
- Inclui verificações adicionais (espaços em branco, fins de arquivo, etc.)

## Instruções de Configuração

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Instalar Hooks de Pre-commit
```bash
pre-commit install
```

### 3. (Opcional) Instalar Hook de Pre-push para Testes
```bash
pre-commit install --hook-type pre-push
```

## Uso Manual

### Format Code with Black
```bash
# Format all Python files
black .

# Format specific file
black app.py

# Check what would be formatted (dry run)
black --check .
```

### Sort Imports with isort
```bash
# Sort all imports
isort .

# Check what would be changed
isort --check-only .
```

### Check Code Quality with Flake8
```bash
# Check all files
flake8

# Check specific file
flake8 app.py
```

### Type Check with mypy
```bash
# Check all files
mypy .

# Check specific file  
mypy app.py

# Check with verbose output
mypy --verbose .
```

### Run All Pre-commit Hooks Manually
```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
```

## What Happens on Commit

When you run `git commit`, the following happens automatically:

1. **Black** formats your Python code
2. **isort** organizes your imports
3. **Flake8** checks for code quality issues
4. **mypy** performs static type checking
5. **Pre-commit hooks** run additional checks:
   - Remove trailing whitespace
   - Fix end-of-file formatting
   - Validate YAML/JSON/TOML files
   - Check for large files
   - Detect merge conflicts
   - Remove debug statements

If any tool finds issues and fixes them, the commit will be stopped. You'll need to review the changes and commit again.

## Configuration Files

- **`.pre-commit-config.yaml`** - Pre-commit hook configuration
- **`pyproject.toml`** - Black formatter and mypy configuration
- **`requirements.txt`** - Includes all formatting and type checking tools

## Benefits

✅ **Consistent Code Style** - All code follows the same formatting rules  
✅ **Automatic Formatting** - No manual formatting needed  
✅ **Quality Assurance** - Catches common issues before they reach the repository  
✅ **Type Safety** - Static type checking prevents runtime type errors  
✅ **Team Collaboration** - Everyone's code looks the same  
✅ **Time Saving** - No debates about formatting in code reviews  

## Skipping Hooks (Emergency Only)

If you need to skip pre-commit hooks in an emergency:
```bash
git commit --no-verify -m "Emergency commit"
```

**Note**: This should be used sparingly and followed up with proper formatting.

## mypy Configuration

The project includes a `mypy.ini` configuration file with strict type checking enabled:
- All functions must have type annotations
- No implicit Optional types allowed
- Warnings for unused imports and redundant casts
- Strict equality checking

mypy runs automatically in CI/CD but can also be run locally:
```bash
mypy .
```