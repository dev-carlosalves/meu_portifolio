"""
blob_storage.py — Cliente HTTP para a Vercel Blob REST API.

Substitui a leitura/escrita de arquivos JSON locais de trilhas pelo
armazenamento gerenciado no Vercel Blob, compatível com o sistema de
arquivos somente-leitura do ambiente de produção da Vercel.

Documentação oficial: https://vercel.com/docs/vercel-blob/rest-api

Uso interno — importe apenas blob_get e blob_put.
"""

from __future__ import annotations

import json
import os
from typing import Optional

import httpx
from dotenv import load_dotenv

# Carrega .env local em desenvolvimento (no-op em produção, onde as vars já
# estão injetadas pelo runtime da Vercel)
load_dotenv()

# ──────────────────────────────────────────────────────────────────────────────
# Configuração
# ──────────────────────────────────────────────────────────────────────────────

_BLOB_API_BASE = "https://blob.vercel-storage.com"

# Cache em memória: pathname → URL pública do blob.
# Evita chamada à list API a cada request; dura até o próximo cold start.
_url_cache: dict[str, str] = {}


def _get_token() -> str:
    """Lê o BLOB_READ_WRITE_TOKEN do ambiente. Levanta RuntimeError se ausente."""
    token = os.environ.get("BLOB_READ_WRITE_TOKEN", "")
    if not token:
        raise RuntimeError(
            "BLOB_READ_WRITE_TOKEN não configurado. "
            "Adicione essa variável ao arquivo .env local e às Environment "
            "Variables do projeto no dashboard da Vercel."
        )
    return token


# ──────────────────────────────────────────────────────────────────────────────
# API pública
# ──────────────────────────────────────────────────────────────────────────────


import time

_data_cache: dict[str, dict] = {}
_data_cache_ts: dict[str, float] = {}


def blob_put(pathname: str, data: dict) -> str:
    """
    Serializa `data` como JSON e faz upload para o Vercel Blob.

    Usa o header `x-add-random-suffix: 0` para manter o pathname
    determinístico: o mesmo nome sempre sobrescreve o mesmo blob,
    comportando-se como um arquivo com nome fixo.

    Args:
        pathname: Caminho/nome do blob (ex: 'trilhas/autocad.json').
        data:     Objeto Python que será serializado para JSON.

    Returns:
        URL pública do blob recém-criado/atualizado.

    Raises:
        RuntimeError: Se BLOB_READ_WRITE_TOKEN não estiver configurado.
        httpx.HTTPStatusError: Em falhas HTTP (4xx/5xx) da API do Blob.
    """
    content = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    url = blob_put_file(pathname, content, content_type="application/json")
    _data_cache[pathname] = data
    _data_cache_ts[pathname] = time.time()
    return url


def blob_put_file(pathname: str, content: bytes, content_type: str = "application/octet-stream") -> str:
    """
    Faz upload de bytes brutos para o Vercel Blob.

    Args:
        pathname:     Caminho/nome do blob (ex: 'trilhas/excel/aula-1/exercicio.xlsx').
        content:      Conteúdo do arquivo em bytes.
        content_type: Tipo MIME do arquivo.

    Returns:
        URL pública do blob.
    """
    token = _get_token()

    from urllib.parse import quote
    safe_pathname = "/".join(quote(part, safe="") for part in pathname.split("/"))

    with httpx.Client(timeout=30.0) as client:
        response = client.put(
            f"{_BLOB_API_BASE}/{safe_pathname}",
            content=content,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": content_type,
                "x-add-random-suffix": "0",
                "x-cache-control-max-age": "0",
            },
        )
        if not response.is_success:
            raise httpx.HTTPStatusError(
                f"Blob file upload falhou ({response.status_code}): {response.text}",
                request=response.request,
                response=response,
            )
        result = response.json()
        url: str = result["url"]
        _url_cache[pathname] = url
        return url




def blob_get(pathname: str) -> Optional[dict]:
    """
    Busca o blob pelo pathname e retorna o conteúdo deserializado como dict.

    Estratégia de localização da URL:
    1. Retorna cache em memória se foi atualizado recentemente via blob_put (evita CDN stale).
    2. Chamada à API / URL pública do Vercel Blob.

    Args:
        pathname: Caminho/nome do blob (ex: 'trilhas/autocad.json').

    Returns:
        Conteúdo do blob como dict, ou None se não existir / JSON inválido.
    """
    # Se foi gravado recentemente (últimos 15s), usa diretamente a memória
    now = time.time()
    if pathname in _data_cache and (now - _data_cache_ts.get(pathname, 0)) < 15.0:
        return _data_cache[pathname]

    try:
        url = _url_cache.get(pathname) or _find_blob_url(pathname)
    except Exception:
        url = None

    if not url:
        return _data_cache.get(pathname)

    _url_cache[pathname] = url  # garante presença no cache para próximas leituras

    # Evita cache intermediário usando timestamp na query
    fresh_url = f"{url}?t={int(now * 1000)}"

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                fresh_url,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )
            if response.status_code == 404:
                # Blob foi deletado externamente → invalida cache
                _url_cache.pop(pathname, None)
                _data_cache.pop(pathname, None)
                _data_cache_ts.pop(pathname, None)
                return None
            response.raise_for_status()
            data = response.json()
            # Só atualiza o cache se não tiver sido gravado localmente mais recentemente
            if (time.time() - _data_cache_ts.get(pathname, 0)) >= 5.0:
                _data_cache[pathname] = data
                _data_cache_ts[pathname] = time.time()
            return _data_cache[pathname]
    except (httpx.HTTPError, json.JSONDecodeError, ValueError):
        return _data_cache.get(pathname)



# ──────────────────────────────────────────────────────────────────────────────
# Interno
# ──────────────────────────────────────────────────────────────────────────────


def _find_blob_url(pathname: str) -> Optional[str]:
    """
    Consulta a list API para encontrar a URL pública de um blob pelo pathname.
    Retorna None se o blob não existir ou a chamada falhar.
    """
    try:
        token = _get_token()
    except Exception:
        return None

    try:
        from urllib.parse import quote
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                _BLOB_API_BASE,
                params={"prefix": pathname, "limit": "10"},
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            blobs = response.json().get("blobs", [])
            for blob in blobs:
                if blob.get("pathname") == pathname:
                    return blob.get("url")
    except Exception:
        pass
    return None
