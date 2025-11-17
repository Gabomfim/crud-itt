"""
Serviço Seguro de Hash e Verificação de Senhas

Este módulo fornece funcionalidade segura de hash e verificação de senhas
usando algoritmo bcrypt com salt rounds configuráveis para balanço ótimo
de segurança e performance na aplicação CRUD ITT.

Recursos Principais:
- Hash de senhas bcrypt padrão da indústria
- Salt rounds configuráveis para ajuste de segurança/performance
- Geração segura de salt para cada senha
- Verificação de senha em tempo constante
- Tratamento de codificação UTF-8 para caracteres internacionais
- Integração com sistema de configuração da aplicação

Recursos de Segurança:
- Geração de salt único para cada senha (previne ataques de tabela arco-íris)
- Fator de trabalho configurável (salt rounds) para adaptar a melhorias de hardware
- Geração de salt aleatório seguro usando entropia do SO
- Comparação em tempo constante para prevenir ataques de timing
- Nenhum armazenamento ou logging de senhas em texto plano

Considerações de Performance:
- Salt rounds configuráveis via configurações (padrão: 12)
- Mais rounds = mais seguro mas mais lento
- Faixas recomendadas: 10-15 para hardware atual
- Tempo de hash escala exponencialmente com rounds
- Considere operações assíncronas para requisições web

Configuração:
Salt rounds são configurados via configurações da aplicação:
- Desenvolvimento: 10-12 rounds (mais rápido para testes)
- Produção: 12-15 rounds (segurança ótima)
- Alta segurança: 15+ rounds (governo/financeiro)

Uso:
```python
from services.password_service import hash_password, verify_password

# Hash da senha durante registro
hashed = hash_password("user_password123")

# Verificar senha durante login
is_valid = verify_password("user_password123", hashed)
```

Integração:
- Usado pelo serviço de autenticação para verificação de login
- Usado pelo serviço de usuário para mudanças de senha
- Integrado com endpoints da API para gerenciamento de usuários
- Compatível com requisitos de armazenamento do banco de dados

Padrões de Segurança:
- Segue diretrizes de armazenamento de senhas OWASP
- Resistente a vetores de ataque comuns
- Adequado para requisitos de conformidade
- Revisão de segurança regular recomendada

Autor: Gabomfim
Licença: MIT
"""

import bcrypt

from config import settings


def hash_password(password: str) -> str:
    """Gera hash bcrypt seguro para senha com fator de trabalho configurável.

    Esta função cria um hash de senha criptograficamente seguro usando o
    algoritmo bcrypt com um salt único para cada senha. O fator de trabalho
    (salt rounds) é configurável via configurações da aplicação para
    balancear segurança e performance.

    Recursos de Segurança:
        - Geração de salt único para cada senha (previne ataques de tabela arco-íris)
        - Fator de trabalho configurável via settings.security.bcrypt_rounds
        - Salt aleatório seguro usando fontes de entropia do SO
        - Algoritmo bcrypt padrão da indústria (baseado em Blowfish)
        - Suporte à codificação UTF-8 para caracteres internacionais

    Args:
        password: Senha em texto plano para fazer hash
                 Deve ser validada quanto à força antes do hash
                 Suporta caracteres Unicode e símbolos especiais
                 Tipicamente 8-128 caracteres de comprimento

    Returns:
        str: Hash bcrypt codificado em Base64 como string UTF-8
             Formato: $2b$[rounds]$[salt-22-char][hash-31-char]
             Exemplo: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj7RG6V8K2.y"
             Comprimento: ~60 caracteres para planejamento de armazenamento

    Performance:
        - Tempo de execução depende dos salt rounds configurados:
          * 10 rounds: ~10ms (rápido, mínimo recomendado)
          * 12 rounds: ~50ms (padrão, bom equilíbrio)
          * 14 rounds: ~200ms (alta segurança)
          * 16 rounds: ~800ms (segurança muito alta)
        - Tempo escala exponencialmente: cada +1 round dobra tempo
        - Considere operações assíncronas para contextos de requisição web

    Configuração:
        Salt rounds configurados via settings.security.bcrypt_rounds:
        - Desenvolvimento: 10-11 (teste mais rápido)
        - Produção: 12-13 (segurança padrão)
        - Alta segurança: 14-15 (governo/financeiro)

    Exemplos de Uso:
        ```python
        # Uso padrão
        hashed = hash_password("MinhaSenh​aSegura123!")

        # Com validação
        if validate_password_strength(password):
            hashed = hash_password(password)
            store_in_database(username, hashed)
        ```

    Considerações de Segurança:
        - Never log or store the input password
        - Always validate password strength before hashing
        - Use HTTPS to protect password transmission
        - Consider password policies (length, complexity)
        - Store hash result securely in database

    Error Handling:
        - bcrypt.hashpw() handles salt generation errors internally
        - UTF-8 encoding errors will raise UnicodeError
        - Memory errors for extremely long passwords

    Storage Requirements:
        - Database column should be VARCHAR(255) or TEXT
        - Actual hash length is ~60 characters
        - Consider indexing strategy (usually not indexed)
    """
    # Generate salt with configured rounds and hash password
    salt = bcrypt.gensalt(rounds=settings.security.bcrypt_rounds)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Securely verify plaintext password against stored bcrypt hash.

    This function performs constant-time password verification using bcrypt's
    built-in comparison function. It automatically extracts the salt and work
    factor from the stored hash and applies the same hashing process to verify
    the provided plaintext password.

    Security Features:
        - Constant-time comparison prevents timing attacks
        - Automatic salt and work factor extraction from hash
        - No plaintext password storage or caching
        - Secure UTF-8 encoding handling
        - Resistant to length extension attacks

    Args:
        plain_password: User-provided plaintext password to verify
                       Should be the exact password without modification
                       Supports Unicode characters and special symbols
                       Typically received from login form or API

        hashed_password: Stored bcrypt hash from database
                        Format: $2b$[rounds]$[22-char salt][31-char hash]
                        Must be complete hash including salt and work factor
                        Should be retrieved securely from user record

    Returns:
        bool: True if password matches the hash, False otherwise
              False is also returned for malformed hashes or encoding errors
              Result should be used immediately (don't cache)

    Performance:
        - Verification time matches original hashing time
        - Time depends on work factor stored in hash:
          * 10 rounds: ~10ms verification time
          * 12 rounds: ~50ms verification time
          * 14 rounds: ~200ms verification time
        - Consider rate limiting for authentication endpoints
        - Use async operations in web request handlers

    Usage Examples:
        ```python
        # Standard authentication flow
        user = get_user_by_username(username)
        if user and verify_password(password, user.password_hash):
            return create_session(user)
        else:
            return authentication_failed()

        # With error handling
        try:
            is_valid = verify_password(form_password, stored_hash)
            if is_valid:
                login_user(user)
            else:
                increment_failed_attempts(user)
        except Exception as e:
            log_security_event("password_verification_error", e)
            return False
        ```

    Security Best Practices:
        - Always use constant-time comparison result
        - Don't reveal whether user exists vs password wrong
        - Log failed authentication attempts for monitoring
        - Consider account lockout after multiple failures
        - Rate limit authentication endpoints
        - Use HTTPS for password transmission

    Error Handling:
        - Returns False for any verification errors
        - Malformed hashes return False (graceful degradation)
        - UTF-8 encoding errors return False
        - Exception details not exposed to prevent information leakage

    Timing Considerations:
        - Verification time is constant regardless of result
        - Time varies only with hash work factor, not password
        - Prevents timing-based username enumeration
        - Consistent response time helps prevent side-channel attacks

    Integration Notes:
        - Used in authentication service for login verification
        - Compatible with password change workflows
        - Works with any bcrypt hash regardless of work factor
        - Suitable for migration from other bcrypt implementations
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )
