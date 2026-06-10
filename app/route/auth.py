from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
import random
import string
import re

router = APIRouter(tags=["Authentication"])
templates = Jinja2Templates(directory="templates")

# Temporary storage for reset codes (in production, use database)
reset_codes = {}


def generate_reset_code():
    """Generate a 6-digit numeric reset code"""
    return ''.join(random.choices(string.digits, k=6))


def is_password_strong(password: str) -> bool:
    """Check if password meets security requirements."""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*]', password):
        return False
    return True


# ============================================================
# LOGIN PAGE
# ============================================================
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request}
    )


@router.post("/login")
async def login(
        request: Request,
        mobile_number: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.mobile_number == mobile_number).first()
    if user and user.password == password:
        request.session["user_id"] = user.id
        request.session["user_name"] = user.full_name
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
            "error": "Invalid mobile number or password"
        }
    )


# ============================================================
# FORGOT PASSWORD - Request Reset Code
# ============================================================
@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="forgot_password.html",
        context={"request": request}
    )


@router.post("/forgot-password")
async def forgot_password(
        request: Request,
        mobile_number: str = Form(...),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.mobile_number == mobile_number).first()
    if not user:
        return templates.TemplateResponse(
            request=request,
            name="forgot_password.html",
            context={
                "request": request,
                "error": "No account found with this mobile number"
            }
        )

    # Generate reset code
    reset_code = generate_reset_code()
    reset_codes[mobile_number] = reset_code

    # In production, send SMS here. For demo, just display the code.
    return templates.TemplateResponse(
        request=request,
        name="reset_password.html",
        context={
            "request": request,
            "mobile_number": mobile_number,
            "reset_code": reset_code,
            "message": f"Reset code generated. (Demo: {reset_code})"
        }
    )


# ============================================================
# RESET PASSWORD - Verify Code and Set New Password
# ============================================================
@router.post("/reset-password")
async def reset_password(
        request: Request,
        mobile_number: str = Form(...),
        reset_code: str = Form(...),
        new_password: str = Form(...),
        confirm_password: str = Form(...),
        db: Session = Depends(get_db)
):
    if new_password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="reset_password.html",
            context={
                "request": request,
                "mobile_number": mobile_number,
                "error": "Passwords do not match"
            }
        )

    # Optional: enforce password strength for reset as well
    if not is_password_strong(new_password):
        return templates.TemplateResponse(
            request=request,
            name="reset_password.html",
            context={
                "request": request,
                "mobile_number": mobile_number,
                "error": "Password must be at least 8 characters and include uppercase, lowercase, digit, and special character (!@#$%^&*)"
            }
        )

    # Verify reset code
    if mobile_number not in reset_codes or reset_codes[mobile_number] != reset_code:
        return templates.TemplateResponse(
            request=request,
            name="reset_password.html",
            context={
                "request": request,
                "mobile_number": mobile_number,
                "error": "Invalid or expired reset code"
            }
        )

    # Update password
    user = db.query(User).filter(User.mobile_number == mobile_number).first()
    if user:
        user.password = new_password
        db.commit()

        # Clear reset code
        del reset_codes[mobile_number]

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "message": "Password reset successful! Please login with your new password."
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="forgot_password.html",
        context={
            "request": request,
            "error": "Something went wrong. Please try again."
        }
    )


# ============================================================
# SIGNUP PAGE
# ============================================================
@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="signup.html",
        context={"request": request}
    )


@router.post("/signup")
async def signup(
        request: Request,
        full_name: str = Form(...),
        mobile_number: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...),
        db: Session = Depends(get_db)
):
    if password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="signup.html",
            context={
                "request": request,
                "error": "Passwords do not match"
            }
        )

    # Enforce strong password on server side
    if not is_password_strong(password):
        return templates.TemplateResponse(
            request=request,
            name="signup.html",
            context={
                "request": request,
                "error": "Password must be at least 8 characters and include uppercase, lowercase, digit, and special character (!@#$%^&*)"
            }
        )

    existing_user = db.query(User).filter(User.mobile_number == mobile_number).first()
    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="signup.html",
            context={
                "request": request,
                "error": "Mobile number already registered"
            }
        )

    new_user = User(
        full_name=full_name,
        mobile_number=mobile_number,
        password=password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    request.session["user_id"] = new_user.id
    request.session["user_name"] = new_user.full_name
    return RedirectResponse(url="/", status_code=303)


# ============================================================
# LOGOUT
# ============================================================
@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)