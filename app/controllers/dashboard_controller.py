from flask import Blueprint, render_template, Response
from app.models.parkir_model import ParkirModel
import cv2
import time

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    data = ParkirModel.get_dashboard_data()
    return render_template("index.html", data=data)


@dashboard_bp.route("/login")
def login():
    return render_template("login.html")
