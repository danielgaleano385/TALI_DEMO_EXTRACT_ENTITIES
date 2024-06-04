from langchain_core.pydantic_v1 import BaseModel, Field
from typing import TypedDict, List, Annotated
from dataclasses import dataclass
from typing import Annotated, Optional


class Persona (BaseModel):
    nombre: str = Field(description="The name of the person")
    direccion: Optional[str] = Field(description="The address of the person")
    codigo_postal: Optional[str] = Field(
        description="The postal code of the person")
    ciudad: Optional[str] = Field(description="The city of the person")
    provincia: Optional[str] = Field(
        description="The province or state of the person")
    pais: Optional[str] = Field(description="The country of the person")
    nacionalidad: Optional[str] = Field(
        description="The nationality of the Person.")
    telefono: Optional[str] = Field(
        description="The phone number of the Person.")
    direcion: Optional[str] = Field(description="The adress of the Person.")


class EmpresaServicios (BaseModel):
    nombre: str = Field(
        description="The name of the company offering the service (essentials such as gas, internet, electricity),product or service")
    direccion_comercial: Optional[str] = Field(
        description="The address of the company")
    cuit: Optional[str] = Field(description="The CUIT of the company")


class Detalles_remito (BaseModel):
    concepto: Optional[str] = Field(
        description="The description of the product or service")
    cantidad: Optional[str] = Field(
        description="The quantity of the product or service")
    precio: Optional[float] = Field(
        description="The price of the product or service")
    importe: Optional[float] = Field(
        description="The total amount of the product or service")


class Factura(BaseModel):
    persona: Persona = Field(description="Description of the Persons")
    empresa: EmpresaServicios = Field(description="Description of the company")
    monto_total: float = Field(
        description="Total amount payable for the service")
    fecha_vencimiento: Optional[str] = Field(
        description="The payment due date")
    periodo_facturado: Optional[str] = Field(description="The billing period")
    detalle: Optional[list[Detalles_remito]] = Field(
        description="The details of the invoice")


class Experiencia (BaseModel):
    empresa: Optional[str] = Field(
        description="The name of the company where you worked or work. Main focus in the work experience section.")
    rol: Optional[str] = Field(
        description="The job title or role in the work, deduce the position of the person in the company in one or tow words")


class Educacion(BaseModel):
    institucion: Optional[str] = Field(
        description="The name of the university or institute, main focus only the name of the institution attention not mention the ubication of the institution.")
    titulo: Optional[str] = Field(
        description="The title of the carrer, `main focus only the name of the carrer` no mather the status of the carrer. Not to mention progress in the carrer. ")


class Idioma(BaseModel):
    idioma: Optional[str] = Field(description="The name of the languaje")
    nivel: Optional[str] = Field(description="Level reached in the language")
    descripcion: Optional[str] = Field(
        description="Whether the level achieved is written or reading level of both or not mentioned")


class ResumenCV (BaseModel):
    persona: Persona = Field(description="Description of the Person")
    experiencias_trabajo: Optional[list[Experiencia]] = Field(
        description="A listed of the person's work experience.")
    educacion: Optional[list[Educacion]] = Field(
        description="List of educational training information.")
    skills: Optional[list[str]] = Field(
        description="Listed a skills include soft skills or tecnicals. Main focus in the skills section. Resume in one or two words.")
    idiomas: Optional[list[Idioma]] = Field(
        description="Listed of the languajes with  the level and describe if know read or talk")
    hobbies: Optional[list[str]] = Field(
        description="Listed the hobbys of the Person")
    linkedin_url: Optional[str] = Field(
        description="The linkedin url of the profile of the Person")
    email: Optional[str] = Field(description="The email of the Person")
