from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, recommendation
from app.simulation import simulate_all_fields
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta

router = APIRouter(tags=["Pages"])
templates = Jinja2Templates(directory="templates")


# ============================================================
# DASHBOARD - Home Page (only current user's fields)
# ============================================================
@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    fields = db.query(models.Field).filter(models.Field.user_id == user_id).all()
    has_fields = len(fields) > 0

    field_data = []
    for field in fields:
        latest, status, action, msg, extra = recommendation.get_recommendation_for_field(db, field)
        if latest:
            moisture = latest.soil_moisture
            since = datetime.utcnow() - timedelta(hours=24)
            readings = db.query(models.SensorReading).filter(
                models.SensorReading.field_id == field.id,
                models.SensorReading.timestamp >= since
            ).all()
            rainfall_24h = readings[-1].rainfall

            if moisture < 20:
                next_watering = "Irrigate today evening"
            elif moisture < 40:
                if rainfall_24h > 5:
                    next_watering = "Delay – rain has helped"
                else:
                    next_watering = "Irrigate tomorrow morning"
            elif moisture <= 70:
                next_watering = "No action needed"
            else:
                next_watering = "Stop irrigating – too wet"

            field_data.append({
                "id": field.id,
                "name": field.name,
                "crop_type": field.crop_type,
                "area_acres": field.area_acres,
                "moisture": moisture,
                "rainfall": rainfall_24h,
                "status": status,
                "next_watering": next_watering,
            })

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "has_fields": has_fields,
            "fields": field_data,
            "page": "dashboard",
            "user_name": request.session.get("user_name")
        }
    )


# ============================================================
# FIELD REPORT (ensure field belongs to current user)
# ============================================================
@router.get("/field/{field_id}", response_class=HTMLResponse)
async def field_report(request: Request, field_id: int, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    field = db.query(models.Field).filter(
        models.Field.id == field_id,
        models.Field.user_id == user_id
    ).first()
    if not field:
        return RedirectResponse(url="/", status_code=303)

    latest, status, action, msg, extra = recommendation.get_recommendation_for_field(db, field)

    since = datetime.utcnow() - timedelta(hours=24)
    readings_24h = db.query(models.SensorReading).filter(
        models.SensorReading.field_id == field_id,
        models.SensorReading.timestamp >= since
    ).all()
    rainfall_24h = sum(r.rainfall for r in readings_24h)

    readings = db.query(models.SensorReading).filter(
        models.SensorReading.field_id == field_id
    ).order_by(models.SensorReading.timestamp.desc()).limit(7).all()
    readings.reverse()
    trend_data = [
        {"timestamp": r.timestamp.strftime("%m/%d %H:%M"), "soil_moisture": r.soil_moisture}
        for r in readings
    ]

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "page": "report",
            "field": field,
            "latest": latest,
            "status": status,
            "action": action,
            "message": msg,
            "rainfall_24h": rainfall_24h,
            "trend_data": trend_data
        }
    )


# ============================================================
# ADD NEW FIELD (user_id already included)
# ============================================================
@router.get("/add-field", response_class=HTMLResponse)
async def add_field_form(request: Request):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"page": "add_field_form", "fields": []}
    )


@router.post("/add-field")
async def add_field(
        request: Request,
        db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    form = await request.form()
    name = form.get("name")
    area = float(form.get("area_acres", 0))
    crop = form.get("crop_type")

    if name and crop:
        field = models.Field(
            name=name,
            area_acres=area,
            crop_type=crop,
            user_id=user_id
        )
        db.add(field)
        db.commit()
        simulate_all_fields(db)
        return RedirectResponse(url="/", status_code=303)
    else:
        return RedirectResponse(url="/add-field?error=missing_fields", status_code=303)


# ============================================================
# DELETE FIELD (only if owned by user)
# ============================================================
@router.post("/delete-field/{field_id}")
async def delete_field(
        request: Request,
        field_id: int,
        db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    field = db.query(models.Field).filter(
        models.Field.id == field_id,
        models.Field.user_id == user_id
    ).first()
    if field:
        db.query(models.SensorReading).filter(models.SensorReading.field_id == field_id).delete()
        db.delete(field)
        db.commit()
    return RedirectResponse(url="/", status_code=303)


# ============================================================
# INITIAL SETUP – first time (no fields) – asks number of fields
# ============================================================
@router.post("/setup")
async def setup_farms(
        request: Request,
        num_fields: int = Form(...),
        db: Session = Depends(get_db)
):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "page": "setup_form",
            "num_fields": num_fields,
            "fields": []
        }
    )


@router.post("/save-fields")
async def save_fields(
        request: Request,
        db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    form = await request.form()
    num_fields = int(form.get("num_fields", 0))

    for i in range(num_fields):
        name = form.get(f"field_{i}_name")
        area = float(form.get(f"field_{i}_area", 0))
        crop = form.get(f"field_{i}_crop")
        if name and crop:
            field = models.Field(
                name=name,
                area_acres=area,
                crop_type=crop,
                user_id=user_id
            )
            db.add(field)

    db.commit()
    simulate_all_fields(db)
    return RedirectResponse(url="/", status_code=303)
