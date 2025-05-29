from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .dependencies import get_db, get_current_user

router = APIRouter()


@router.post("/receipts", response_model=schemas.ReceiptOutput)
def create_receipt(
    receipt_data: schemas.ReceiptCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    total_sum = 0
    items = []

    for product in receipt_data.products:
        line_total = product.price * product.quantity
        total_sum += line_total
        items.append({
            "name": product.name,
            "price": product.price,
            "quantity": product.quantity,
            "total": line_total
        })

    if receipt_data.payment.amount < total_sum:
        raise HTTPException(
            status_code=400, detail="Insufficient payment amount."
        )

    rest = receipt_data.payment.amount - total_sum

    receipt = models.Receipt(
        user_id=user.id,
        payment_type=receipt_data.payment.type.value,
        payment_amount=receipt_data.payment.amount,
        total=total_sum,
        rest=rest
    )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)

    for item in items:
        db_item = models.ReceiptItem(
            receipt_id=receipt.id,
            name=item["name"],
            price=item["price"],
            quantity=item["quantity"],
            total=item["total"]
        )
        db.add(db_item)

    db.commit()
    db.refresh(receipt)

    return schemas.ReceiptOutput(
        id=receipt.id,
        products=items,
        payment=schemas.PaymentOutput(
            type=receipt.payment_type, amount=receipt.payment_amount
        ),
        total=total_sum,
        rest=rest,
        created_at=receipt.created_at
    )
