from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.config import settings
from app.controllers.workspace import router

app = FastAPI(title='Meridian 框架 API（演示）', version='0.1.0', description='仅框架与演示业务；认证、正式数据契约和外部集成尚未实现。')
app.include_router(router)


@app.exception_handler(HTTPException)
async def http_error(_request, exc):
    code = {409: 'E2002', 422: 'E2004', 503: 'E0001'}.get(exc.status_code, 'E0000')
    return JSONResponse(status_code=exc.status_code, content={'code': code, 'message': str(exc.detail), 'data': None})


@app.exception_handler(RequestValidationError)
async def validation_error(_request, _exc):
    return JSONResponse(status_code=422, content={'code': 'E2004', 'message': '请求参数错误', 'data': None})


@app.get('/api/v1/health', tags=['system'])
def health():
    return {'code': 0, 'message': 'ok', 'data': {'status': 'up', 'demo_mode': settings.app_demo_mode, 'crawl_enabled': False, 'integrations': 'not_configured'}}
