"""
Ponto de Entrada da Aplicação FastAPI

Este módulo contém a configuração e setup principal da aplicação FastAPI.
Ele inicializa o banco de dados, configura middleware, configura roteamento, e
gerencia eventos do ciclo de vida da aplicação.

Recursos Principais:
- Inicialização assíncrona do banco de dados
- Configuração de middleware CORS
- Logging de requisições e middleware de verificação de saúde
- Servir arquivos estáticos e renderização de templates HTML
- Tratamento customizado de erro 404
- Setup abrangente de logging

Autor: Gabomfim
Licença: MIT
"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import Response as StarletteResponse
from starlette.templating import _TemplateResponse

from api.v1.api import api_router
from config import settings
from database.connection import init_database
from utils.logging_config import get_logger, setup_logging
from utils.middleware import HealthCheckMiddleware, RequestLoggingMiddleware


def render_template(
    request: Request, template_name: str, status_code: int = 200
) -> _TemplateResponse:
    """Função auxiliar para renderizar templates com tipagem adequada"""
    return templates.TemplateResponse(
        request, template_name, status_code=status_code
    )  # type: ignore


# Configurar logging usando configurações Pydantic
setup_logging(app_name=settings.app.name)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Gerenciar o ciclo de vida da aplicação com eventos de startup e shutdown.

    Esta função trata da inicialização do banco de dados no startup e limpeza
    no shutdown. Ela usa um gerenciador de contexto assíncrono para garantir
    gerenciamento adequado de recursos.

    Args:
        app (FastAPI): A instância da aplicação FastAPI

    Yields:
        None: O controle é cedido durante a execução da aplicação

    Raises:
        Exception: Qualquer exceção durante a inicialização do banco de dados

    Example:
        Esta função é automaticamente chamada pelo FastAPI durante
        o startup e shutdown da aplicação.
    """
    # Logar startup da aplicação
    logger.info("Aplicação iniciando")

    try:
        # Inicializar banco de dados no startup
        await init_database()
        logger.info("Banco de dados inicializado com sucesso")
    except Exception as e:
        logger.error(
            "Falha ao inicializar banco de dados",
            extra={"error": str(e)},
            exc_info=True,
        )
        raise

    logger.info("Startup da aplicação completado")
    yield

    # Logar shutdown da aplicação
    logger.info("Aplicação desligando")


app = FastAPI(
    title=settings.app.name,
    description=settings.app.description,
    version=settings.app.version,
    debug=settings.app.debug,
    lifespan=lifespan,
)

# Adicionar middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.cors_origins,
    allow_credentials=True,
    allow_methods=settings.app.cors_methods,
    allow_headers=settings.app.cors_headers,
)

# Adicionar middleware de logging
app.add_middleware(RequestLoggingMiddleware, exclude_paths=["/health", "/metrics"])
app.add_middleware(HealthCheckMiddleware, health_path="/health")

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Incluir rotas da API v1
app.include_router(api_router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request) -> StarletteResponse:
    """
    Servir a página HTML raiz da aplicação.

    Este endpoint serve a página principal usando templates Jinja2.
    Ele fornece uma interface amigável com informações da aplicação
    e links de navegação.

    Args:
        request (Request): O objeto de requisição FastAPI contendo informações do
            cliente

    Returns:
        StarletteResponse: Template HTML renderizado com conteúdo da aplicação

    Example:
        GET / HTTP/1.1
        Host: localhost:8000

        Response: Página HTML com interface da aplicação
    """
    logger.info("Servindo página raiz")
    return render_template(request, "index.html")


# Manipulador de erro customizado apenas para 404s não-API
@app.middleware("http")
async def custom_404_middleware(
    request: Request, call_next: Callable[[Request], Any]
) -> Response:
    """
    Middleware customizado para tratar erros 404 com respostas HTML.

    Este middleware intercepta erros 404 e retorna uma página HTML
    de erro customizada quando o cliente acessa rotas não-API. Para requisições de API,
    ele deixa a resposta JSON de erro padrão passar.

    Args:
        request (Request): A requisição HTTP de entrada
        call_next (Callable): O próximo middleware ou endpoint na cadeia

    Returns:
        Response: Ou a resposta original ou página HTML 404 customizada

    Raises:
        Exception: Re-levanta qualquer exceção não tratada após logar

    Example:
        GET /nonexistent-page HTTP/1.1
        Accept: text/html

        Response: Página HTML 404 customizada
    """
    try:
        response = await call_next(request)
        # Se é um 404 em uma rota não-API, retornar página HTML customizada
        if response.status_code == 404 and not request.url.path.startswith("/api/"):
            logger.info(
                "Servindo página 404 customizada",
                extra={"path": request.url.path, "method": request.method},
            )
            return render_template(request, "404.html", status_code=404)
        return response  # type: ignore
    except Exception as e:
        logger.error(
            "Exceção não tratada no middleware",
            extra={"path": request.url.path, "method": request.method, "error": str(e)},
            exc_info=True,
        )
        # Deixar FastAPI tratar todas as exceções normalmente
        raise e
