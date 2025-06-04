from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ---------- Usuario ----------
class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    senha: Optional[str] = None
    role_id: Optional[int]
    ativo: Optional[bool] = None
    class Config:
        orm_mode = True

class UsuarioOut(UsuarioBase):
    id: int
    class Config:
        from_attributes = True


# ---------- Role ----------
class RoleBase(BaseModel):
    nome: str

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    nome: Optional[str] = None

class RoleOut(RoleBase):
    id: int
    class Config:
        from_attributes = True


# ---------- Empresa ----------
class EmpresaBase(BaseModel):
    nome: str

class EmpresaCreate(EmpresaBase):
    pass

class EmpresaUpdate(BaseModel):
    nome: Optional[str] = None

class EmpresaOut(EmpresaBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True


# ---------- Maquina ----------
class MaquinaBase(BaseModel):
    modelo: str

class MaquinaCreate(MaquinaBase):
    pass

class MaquinaUpdate(BaseModel):
    modelo: Optional[str] = None

class MaquinaOut(MaquinaBase):
    id: int

    class Config:
        from_attributes = True

# ---------- OrigemProblema ----------
class OrigemProblemaBase(BaseModel):
    nome: str

class OrigemProblemaCreate(OrigemProblemaBase):
    pass

class OrigemProblemaUpdate(BaseModel):
    nome: Optional[str] = None

class OrigemProblemaOut(OrigemProblemaBase):
    id: int
    class Config:
        from_attributes = True


# ---------- Prioridade ----------
class PrioridadeBase(BaseModel):
    nome: str

class PrioridadeCreate(PrioridadeBase):
    pass

class PrioridadeUpdate(BaseModel):
    nome: Optional[str] = None

class PrioridadeOut(PrioridadeBase):
    id: int
    class Config:
        from_attributes = True


# ---------- Status ----------
class StatusBase(BaseModel):
    nome: str

class StatusCreate(StatusBase):
    pass

class StatusUpdate(BaseModel):
    nome: Optional[str] = None

class StatusOut(StatusBase):
    id: int
    class Config:
        from_attributes = True


# ---------- Frequencia ----------
class FrequenciaBase(BaseModel):
    nome: str

class FrequenciaCreate(FrequenciaBase):
    pass

class FrequenciaUpdate(BaseModel):
    nome: Optional[str] = None

class FrequenciaOut(FrequenciaBase):
    id: int
    class Config:
        from_attributes = True


# ---------- Chamado ----------
class ChamadoBase(BaseModel):
    cliente: str
    relato: str
    porta_ssh: Optional[str] = None
    descricao_acao: Optional[str] = None
    prioridade_id: Optional[int] = None
    status_id: Optional[int] = 1
    empresa_id: Optional[int] = None
    tipo_maquina_id: Optional[int] = None
    origem_id: Optional[int] = None
    responsavel_atendimento_id: Optional[int] = None
    responsavel_acao_id: Optional[int] = None

class ChamadoCreate(ChamadoBase):
    pass

class ChamadoUpdate(ChamadoBase):
    pass

class ChamadoOut(ChamadoBase):
    id: int
    datetime_abertura: Optional[datetime]
    class Config:
        from_attributes = True


# ---------- ChamadoRecorrente ----------
class ChamadoRecorrenteBase(BaseModel):
    cliente: str
    porta_ssh: Optional[str]
    relato: str
    descricao_acao: Optional[str]
    prioridade_id: Optional[int]
    empresa_id: Optional[int]
    tipo_maquina_id: Optional[int]
    origem_id: Optional[int]
    responsavel_atendimento_id: Optional[int]
    responsavel_acao_id: Optional[int]
    frequencia_id: int
    proxima_execucao: datetime

class ChamadoRecorrenteCreate(ChamadoRecorrenteBase):
    pass

class ChamadoRecorrenteUpdate(BaseModel):
    cliente: Optional[str] = None
    porta_ssh: Optional[str] = None
    relato: Optional[str] = None
    descricao_acao: Optional[str] = None
    prioridade_id: Optional[int] = None
    empresa_id: Optional[int] = None
    tipo_maquina_id: Optional[int] = None
    origem_id: Optional[int] = None
    responsavel_atendimento_id: Optional[int] = None
    responsavel_acao_id: Optional[int] = None
    frequencia_id: Optional[int] = None
    proxima_execucao: Optional[datetime] = None

class ChamadoRecorrenteOut(ChamadoRecorrenteBase):
    id: int
    class Config:
        from_attributes = True


# ---------- LogAcao ----------
class LogAcaoBase(BaseModel):
    acao: str
    tipo: Optional[str]
    campo: Optional[str]
    valor_antigo: Optional[str]
    valor_novo: Optional[str]
    usuario_id: Optional[int]
    chamado_id: Optional[int]

class LogAcaoCreate(LogAcaoBase):
    pass

class LogAcaoOut(LogAcaoBase):
    id: int
    data_hora: datetime
    class Config:
        from_attributes = True
