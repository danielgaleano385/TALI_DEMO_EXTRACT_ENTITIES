from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Annotated
from dataclasses import dataclass
from typing import Annotated, Optional
from langchain.document_loaders import PyPDFLoader
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI
from langchain.chains import create_extraction_chain_pydantic
import os
import dotenv
import json
from model import *

_ = dotenv.load_dotenv()
OPEN_IA_KEY = os.getenv("OPEN_IA_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY


@dataclass()
class config:
    verbose: bool = True
    model_name: str = "gpt-3.5-turbo"
    path_dir: str = "data/data_extractor"
    file_name: str = "data.pdf"

    def path_file(self):
        return os.path.join(self.path_dir, self.file_name)


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        reoute: route extractor
        extractor: LLM extractor
        documents: list of documents
    """

    route: str
    extractor: str
    documents: List[str]


class graph ():
    def __init__(self) -> None:
        self.config = config()
        self.workflow = StateGraph(GraphState)
        self.app = self.create_workflow()

    def create_workflow(self):
        def PDFinfoExtractor(state):
            print("---PDF Info Extractor---")
            loader = PyPDFLoader(self.config.path_file(), extract_images=True)
            documents = loader.load_and_split()
            return {"documents": documents}

        def routeExtractor(state):
            print("---Route Direction---")

            prompt = """You are an expert in classifying documents in the following context and choosing the most appropriate way to process them. 
            You must classify the document in one of the following possibilities: 
             - Curriculum Vitae-Hoja de Vida
             - Remito-Factura 
            Important if you do not have a high certainty that of the two types of documents requested,  classify as 
             - Other
            
            Do not answer with more than one word.

            <context>
            {documents}
            </context>

            Classification:
            """

            llm = ChatOpenAI(openai_api_key=OPEN_IA_KEY,
                             model_name=config.model_name)

            documents = state["documents"]

            route_template = PromptTemplate.from_template(prompt)

            output_parser = StrOutputParser()

            chain = route_template | llm | output_parser

            route = chain.invoke({"documents": documents})
            print(route)
            return {"route": route}

        def facturaExtractor(state):
            print("---Factura Remito Extractor---")
            llm = ChatOpenAI(openai_api_key=OPEN_IA_KEY,
                             model_name=self.config.model_name)

            chain = create_extraction_chain_pydantic(
                pydantic_schema=Factura,
                llm=llm,
                verbose=self.config.verbose
            )
            with get_openai_callback() as cb:
                extractor = chain.run(state["documents"])
                print(f"Total token: {cb.total_tokens}")
                print(f"Prompt token: {cb.prompt_tokens}")
                print(f"Prompt token: {cb.completion_tokens}")
                print(f"Total cost: ${cb.total_cost}")

            return {"extractor": extractor}

        def cvExtractor(state):
            print("---CV Extractor---")
            llm = ChatOpenAI(openai_api_key=OPEN_IA_KEY,
                             model_name=config.model_name)

            chain = create_extraction_chain_pydantic(ResumenCV,
                                                     llm=llm,
                                                     verbose=self.config.verbose
                                                     )
            with get_openai_callback() as cb:
                extractor = chain.run(state["documents"])
                print(f"Total token: {cb.total_tokens}")
                print(f"Prompt token: {cb.prompt_tokens}")
                print(f"Prompt token: {cb.completion_tokens}")
                print(f"Total cost: ${cb.total_cost}")

            return {"extractor": extractor}

        def decideRoute(state):
            print("---Decide Documento---")

            if state["route"] == "Remito-Factura":
                return "facturaExtractor"
            if state["route"] == "Curriculum Vitae-Hoja de Vida":
                return "cvExtractor"
            else:
                return "Other"

        def parseOutput(state):

            print("---Parse Output---")
            if state.get("route"):
                route = state["route"]
            entities = state["extractor"][0]
            if route == "Curriculum Vitae-Hoja de Vida":
                print("---CV Parsing---")
                entities = dict(entities)
                entities["persona"] = dict(
                    entities["persona"]) if entities.get("persona") else None
                if entities.get("experiencias_trabajo"):
                    entities["experiencias_trabajo"] = [
                        dict(experiencia) for experiencia in entities["experiencias_trabajo"]]
                if entities.get("educacion"):
                    entities["educacion"] = [dict(educacion)
                                             for educacion in entities["educacion"]]
                if entities.get("idiomas"):
                    entities["idiomas"] = [dict(idioma)
                                           for idioma in entities["idiomas"]]

            if route == "Remito-Factura":
                print("---Factura Parsing---")
                entities = dict(entities)
                entities["persona"] = dict(
                    entities["persona"]) if entities.get("persona") else None
                entities["empresa"] = dict(
                    entities["empresa"]) if entities.get("empresa") else None
                entities["detalle"] = [dict(detalle)
                                       for detalle in entities["detalle"]]
            return {"extractor": entities}

        self.workflow.add_node("PDFinfoExtractor", PDFinfoExtractor)
        self.workflow.add_node("routeExtractor", routeExtractor)
        self.workflow.add_node("facturaExtractor", facturaExtractor)
        self.workflow.add_node("cvExtractor", cvExtractor)
        self.workflow.add_node("output", parseOutput)
        # conexiones
        self.workflow.set_entry_point("PDFinfoExtractor")
        self.workflow.add_edge("PDFinfoExtractor", "routeExtractor")
        self.workflow.add_conditional_edges("routeExtractor", decideRoute, {
            "facturaExtractor": "facturaExtractor",
            "cvExtractor": "cvExtractor",
            "Other": END
        })

        self.workflow.add_edge("facturaExtractor", "output")
        self.workflow.add_edge("cvExtractor", "output")
        self.workflow.add_edge("output", END)
        return self.workflow.compile()
