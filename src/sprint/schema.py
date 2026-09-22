"""The shape we want back. This class IS the contract.

pydantic turns it into a JSON Schema, and the API constrains generation to fit —
the model cannot return a different shape. Java: the target type you hand
Jackson, except the upstream is forced to comply instead of merely expected to.
"""

from pydantic import BaseModel, Field


class Invoice(BaseModel):
    """One extracted invoice.

    NOTE: the descriptions below are deliberately naive — a first draft.
    They are sent to the model as part of the schema, so they ARE the prompt.
    Today's job is to find out where they fail. Improving them is the fix,
    and it's an English edit, not a Python one.
    """

    invoice_number: str = Field(description="The invoice number")
    invoice_date: str = Field(description="The invoice date")
    vendor_name: str = Field(
        description="The company ISSUING this invoice — the one being paid. "
                    "NOT the customer or 'Bill To' party."
    )
    total_amount: float = Field(description="The total amount")