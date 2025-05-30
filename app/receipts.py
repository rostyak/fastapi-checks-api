from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from starlette.responses import PlainTextResponse

from . import models, schemas
from .dependencies import get_db, get_current_user
from .models import User, Receipt
from .schemas import PaymentType

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


@router.get("/receipts", response_model=List[schemas.ReceiptOutput])
def get_receipts(
    created_from: Optional[datetime] = Query(None),
    created_to: Optional[datetime] = Query(None),
    total_min: Optional[float] = Query(None),
    total_max: Optional[float] = Query(None),
    payment_type: Optional[PaymentType] = Query(None),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(
        Receipt
    ).options(
        selectinload(Receipt.items)
    ).filter(
        Receipt.user_id == current_user.id
    )

    if created_from:
        query = query.filter(Receipt.created_at >= created_from)
    if created_to:
        query = query.filter(Receipt.created_at <= created_to)
    if total_min is not None:
        query = query.filter(Receipt.total >= total_min)
    if total_max is not None:
        query = query.filter(Receipt.total <= total_max)
    if payment_type:
        query = query.filter(Receipt.payment_type == payment_type)

    receipts = query.order_by(
        Receipt.created_at.desc()
    ).offset(offset).limit(limit).all()

    result = []

    for receipt in receipts:
        products = [
            schemas.ProductOutput(
                name=item.name,
                price=item.price,
                quantity=item.quantity,
                total=item.total
            )
            for item in receipt.items
        ]

        payment = schemas.PaymentOutput(
            type=receipt.payment_type,
            amount=receipt.payment_amount
        )

        result.append(
            schemas.ReceiptOutput(
                id=receipt.id,
                products=products,
                payment=payment,
                total=receipt.total,
                rest=receipt.rest,
                created_at=receipt.created_at
            )
        )

    return result


@router.get("/receipts/{receipt_id}", response_model=schemas.ReceiptOutput)
def get_receipt_by_id(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    receipt = db.query(
        Receipt
    ).options(
        selectinload(Receipt.items)
    ).filter(
        Receipt.id == receipt_id,
        Receipt.user_id == current_user.id
    ).first()

    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    products = [
        schemas.ProductOutput(
            name=item.name,
            price=item.price,
            quantity=item.quantity,
            total=item.total
        )
        for item in receipt.items
    ]

    payment = schemas.PaymentOutput(
        type=receipt.payment_type,
        amount=receipt.payment_amount
    )

    return schemas.ReceiptOutput(
        id=receipt.id,
        products=products,
        payment=payment,
        total=receipt.total,
        rest=receipt.rest,
        created_at=receipt.created_at
    )


@router.get("/public/receipt/{public_token}", response_class=PlainTextResponse)
def view_public_receipt(
    public_token: str,
    # Set minimum line width (for correct header and footer alignment)
    line_width: int = Query(40, ge=20, le=120),
    db: Session = Depends(get_db)
):
    receipt = db.query(
        Receipt
    ).options(
        selectinload(Receipt.items)
    ).filter_by(
        public_token=public_token
    ).first()

    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    def format_line(text: str, value: str = "", width: int = line_width):
        max_item_name_len = 14

        if len(text) > max_item_name_len:
            text = text[:max_item_name_len - 3] + "..."

        space = width - len(text) - len(value)

        return f"{text}{' ' * max(1, space)}{value}"

    # Add headers
    lines = [
        "ФОП Джонсонюк Борис".center(line_width),
        "=" * line_width
    ]

    # Add items
    for item in receipt.items:
        qty_price = (
            f"{item.quantity:.2f} x {item.price:,.2f}".replace(",", " ")
        )
        lines.append(qty_price)

        name = item.name.strip()
        name_line = format_line(
            name, f"{item.total:,.2f}".replace(",", " ")
        )

        lines.append(name_line)
        lines.append("-" * line_width)

    lines.append("=" * line_width)

    # Add totals
    lines.append(format_line(
        "СУМА", f"{receipt.total:,.2f}".replace(",", " ")
    ))
    lines.append(format_line(
        "Картка", f"{receipt.payment_amount:,.2f}".replace(",", " ")
    ))
    lines.append(format_line(
        "Решта", f"{receipt.rest:,.2f}".replace(",", " ")
    ))
    lines.append("=" * line_width)

    # Add footer
    lines.append(
        receipt.created_at.strftime("%d.%m.%Y %H:%M").center(line_width)
    )
    lines.append("Дякуємо за покупку!".center(line_width))

    max_len_line = max(len(line) for line in lines)

    # Check is the longest line exceeds the specified width - if True, return
    # the receipt with the maximum line width
    if max_len_line > line_width:
        return view_public_receipt(
            public_token, line_width=max_len_line, db=db
        )

    return "\n".join(lines)
