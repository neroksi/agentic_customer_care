import re
from datetime import date
from typing import Any, Literal, Optional

import pandas as pd
from pydantic import BaseModel as pBaseModel

DELIVERY_STATUS = Literal[
    "DELIVERED", "AT_CHECKPOINT", "IN_TRANSIT", "CANCELLED", "RETURNED"
]
CURRENCY = Literal["USD", "EUR", "GBP", "CHF", "JPY", "CNY"]


def clean_field_name(field_name: str) -> str:
    return re.sub(r"[^a-z]", "", field_name.lower())


class BaseModel(pBaseModel):
    """
    Base data model, with some helper methods for object instantiation from dicts.
    """

    @classmethod
    def retrieve_raw_field_values(
        cls, data: dict[str, Any], strict: bool = True
    ) -> dict[str, Any]:

        data_keys = {clean_field_name(key): key for key in data}
        field_values: dict[str, Any] = {}

        for field_name in cls.model_fields:
            field_name_ = clean_field_name(field_name)
            try:
                field_values[field_name] = data[data_keys[field_name_]]
            except KeyError as e:
                if strict:
                    raise ValueError(f"Field {field_name} not found in data") from e

        return field_values

    @classmethod
    def preprocess_raw_field_values(
        cls, raw_field_values: dict[str, Any]
    ) -> dict[str, Any]:
        return raw_field_values

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], *, strict: bool | None = None, **kwargs: Any
    ):
        strict = not bool(kwargs) if strict is None else strict
        raw_field_values = cls.retrieve_raw_field_values(data, strict=strict)
        raw_field_values.update(kwargs)
        return cls(**cls.preprocess_raw_field_values(raw_field_values))


class Product(BaseModel):
    id: str
    name: str
    short_description: str
    color: str
    size: str
    origin_country: str
    delivrable_countries: list[str]
    universe: str

    @classmethod
    def preprocess_raw_field_values(cls, raw_field_values: dict[str, Any]):
        """Ensure delivrable_countries is a list of strings"""

        raw_field_values["delivrable_countries"] = re.split(
            r"\s*[,;]\s*", raw_field_values["delivrable_countries"]
        )
        return raw_field_values


class Delivery(BaseModel):
    id: str
    status: DELIVERY_STATUS
    sent_date: date
    planned_delivery_date: date
    effective_delivery_date: Optional[date]
    any_delivery_issue: bool
    delivery_country: str


class OrderItem(BaseModel):
    id: str
    product: Product
    quantity: int
    unit_price: float
    currency: CURRENCY


class Order(BaseModel):
    id: str
    date: date
    items: list[OrderItem]
    deliveries: list[Delivery]


class Customer(BaseModel):
    id: str
    name: str
    email: str
    country: str
    orders: list[Order]


def build_crm_data(
    customer_df: pd.DataFrame,
    product_df: pd.DataFrame,
    order_df: pd.DataFrame,
    order_item_df: pd.DataFrame,
    delivery_df: pd.DataFrame,
) -> dict[str, Customer]:

    products_dict = {
        product_dict["Id"]: Product.from_dict(product_dict)  # type: ignore
        for product_dict in product_df.to_dict(orient="records")  # type: ignore
    }

    crm_data: dict[str, Customer] = {}

    for customer_dict in customer_df.to_dict(orient="records"):  # type: ignore

        orders: list[Order] = []

        for order_dict in order_df.query("CustomerId == @customer_dict['Id']").to_dict(  # type: ignore
            orient="records"
        ):
            items = [
                OrderItem.from_dict(
                    order_item_dict, product=products_dict[order_item_dict["ProductId"]]  # type: ignore
                )
                for order_item_dict in order_item_df.query(  # type: ignore
                    "OrderId == @order_dict['Id']"
                ).to_dict(orient="records")
            ]

            deliveries = [
                Delivery.from_dict(delivery_dict)  # type: ignore
                for delivery_dict in delivery_df.query(  # type: ignore
                    "OrderId == @order_dict['Id']"
                ).to_dict(orient="records")
            ]
            order = Order.from_dict(order_dict, items=items, deliveries=deliveries)  # type: ignore

            orders.append(order)

        customer = Customer.from_dict(customer_dict, orders=orders)  # type: ignore
        crm_data[customer.id] = customer

    return crm_data
