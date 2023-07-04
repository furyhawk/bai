# Fastapi application entry point
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi import Request
from fastapi import Form
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBasic
from fastapi.security import HTTPBasicCredentials
from fastapi.security import OAuth2
from fastapi.security import SecurityScopes
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.docs import get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowImplicit as OAuthFlowImplicitModel
from fastapi.openapi.models import OAuthFlowPassword as OAuthFlowPasswordModel
from fastapi.openapi.models import OAuthFlowClientCredentials as OAuthFlowClientCredentialsModel
from fastapi.openapi.models import OAuthFlowAuthorizationCode as OAuthFlowAuthorizationCodeModel
from fastapi.openapi.models import SecurityRequirement as SecurityRequirementModel
from fastapi.openapi.models import SecurityScheme as SecuritySchemeModel
from fastapi.security.utils import get_authorization_scheme_param

from pydantic import BaseModel
from pydantic import Field
from pydantic import EmailStr
from pydantic import validator
from pydantic import ValidationError

from typing import Optional
from typing import List
from typing import Dict
from typing import Any
from typing import Union
from typing import Tuple
from typing import Callable
from typing import Generator
from typing import Literal
from typing import cast

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from jose import JWTError
from jose import jwt

from passlib.context import CryptContext

from starlette.responses import RedirectResponse
from starlette.responses import Response
from starlette.responses import JSONResponse
from starlette.responses import StreamingResponse
from starlette.responses import FileResponse
from starlette.responses import HTMLResponse
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.status import HTTP_403_FORBIDDEN
from starlette.status import HTTP_404_NOT_FOUND
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

from starlette.middleware.sessions import SessionMiddleware

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint

from starlette.staticfiles import StaticFiles

from starlette_context import context

from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import SessionLocal
from sqlalchemy import create_engine
from sqlalchemy import engine_from_config
from sqlalchemy import event
from sqlalchemy import exc
from sqlalchemy import select
from sqlalchemy import func

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import DeferredReflection
from sqlalchemy.ext.declarative import declared_attr

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy import Index
from sqlalchemy import text
from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy import not_
from sqlalchemy import func
from sqlalchemy import desc
from sqlalchemy import asc
from sqlalchemy import event
from sqlalchemy import exc
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy import literal
from sqlalchemy import literal_column
from sqlalchemy import case
from sqlalchemy import cast
from sqlalchemy import distinct
from sqlalchemy import union
from sqlalchemy import union_all
from sqlalchemy import intersect
from sqlalchemy import except_
from sqlalchemy import join
from sqlalchemy import outerjoin
from sqlalchemy import subquery
from sqlalchemy import exists
from sqlalchemy import update
from sqlalchemy import delete
from sqlalchemy import insert
from sqlalchemy import Table
from sqlalchemy import MetaData
from sqlalchemy import inspect
from sqlalchemy import create_engine
from sqlalchemy import engine_from_config
from sqlalchemy import event
from sqlalchemy import exc
from sqlalchemy import select


from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import aliased
from sqlalchemy.orm import with_polymorphic
from sqlalchemy.orm import mapper
from sqlalchemy.orm import configure_mappers




