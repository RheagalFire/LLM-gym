from gym_reader.agents.semantic_answer import ContextAwareAnswerAgent
from typing import Type, Any, Dict, Optional
from pydantic import BaseModel, Field, create_model


agents = [ContextAwareAnswerAgent]

_initialized = False  # Module-level flag to ensure initialization runs only once


def init_agentic_mappers():
    global _initialized
    if not _initialized:
        agent_dict = {}
        for agent in agents:
            agent_init = agent()
            agent_dict[agent_init.class_name] = {
                "class_name": agent_init.class_name,
                "description": agent_init.desc,
                "input_variables": agent_init.input_variables,
                "class_object": agent_init,
            }
        _initialized = True
    return agent_dict


agent_dict = init_agentic_mappers()


def create_pydantic_model_from_signature(
    signature_cls: Type[Any], model_name: str = "DynamicOutputModel"
) -> Type[BaseModel]:
    """
    Dynamically creates a Pydantic model from a dspy.Signature class by extracting output fields.

    Args:
        signature_cls (Type[Any]): The signature class from which to extract fields.
        model_name (str): The name of the Pydantic model to create.

    Returns:
        Type[BaseModel]: The dynamically created Pydantic model.
    """
    fields: Dict[str, tuple] = {}

    for name, field_info in signature_cls.model_fields.items():
        # Check if the field is an output field
        if field_info.json_schema_extra.get("__dspy_field_type") == "output":
            # Map the field type
            pydantic_type = field_info.annotation

            # Determine if the field is optional
            if not field_info.is_required():
                pydantic_type = Optional[pydantic_type]
                default = None
            else:
                default = ...

            # Add the field to the model with its type and description
            fields[name] = (
                pydantic_type,
                Field(default, description=field_info.json_schema_extra["desc"]),
            )

    # Create the Pydantic model
    DynamicModel = create_model(model_name, **fields)

    return DynamicModel
