# -*- coding: utf-8 -*-
"""
Manifest Route
==============

/.well-known/aiw-manifest.json 엔드포인트.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.opstwin.aiw.manifest import build_manifest

router = APIRouter(tags=["AIW Protocol"])


@router.get("/.well-known/aiw-manifest.json")
async def get_manifest():
    """AIW Manifest 반환 (서비스 디스커버리)"""
    manifest = build_manifest()
    return JSONResponse(
        content=manifest,
        media_type="application/json",
    )


@router.get("/schemas")
async def list_schemas():
    """스키마 레지스트리 목록"""
    from src.opstwin.aiw.schema_registry import schema_registry

    return {"schemas": schema_registry.list_schemas()}


@router.get("/schemas/{name}")
async def get_schema(name: str):
    """특정 스키마 조회"""
    from src.opstwin.aiw.schema_registry import schema_registry

    schema = schema_registry.get_schema(name)
    if schema is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Schema not found: {name}"},
        )
    return schema
