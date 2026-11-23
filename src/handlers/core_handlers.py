from flask import Blueprint, g, jsonify, redirect, render_template, request, url_for
from flask.views import MethodView

from src.dao.core_dao import PostgresUserDAO, PostgresVisitorLogDAO
from src.dao.inventory_dao import PostgresBookDAO, PostgresInterestDAO, PostgresItemDAO
from src.dtos.core_dtos import LoginDTO, UserRegistrationDTO, VisitorLogDTO
from src.exceptions.core_exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    VisitorLogCreationError,
)
from src.services.core_service import CoreService
from src.services.inventory_service import InventoryService

core_bp = Blueprint("core", __name__)

_user_dao = PostgresUserDAO()
_visitor_log_dao = PostgresVisitorLogDAO()
_core_service = CoreService(
    user_dao=_user_dao,
    visitor_log_dao=_visitor_log_dao,
)

_book_dao = PostgresBookDAO()
_item_dao = PostgresItemDAO()
_interest_dao = PostgresInterestDAO()

_inventory_service = InventoryService(
    book_dao=_book_dao,
    item_dao=_item_dao,
    interest_dao=_interest_dao,
)


class IndexHandler(MethodView):
    def get(self):
        interested_books = []
        visitor_data = None

        if g.user_id:
            interested_books = _inventory_service.get_user_interested_books(g.user_id)

        if g.user_role == "ADMIN":
            search_name = request.args.get("q", "")
            try:
                page = max(1, int(request.args.get("page", 1)))
            except ValueError:
                page = 1

            visitor_data = _core_service.get_visitor_logs(
                search_name=search_name, page=page, per_page=8
            )

        return render_template(
            "core/index.html",
            interested_books=interested_books,
            visitor_data=visitor_data,
        )


class RegistrationHandler(MethodView):
    def get(self):
        return render_template("auth/register.html")

    def post(self):
        try:
            json_data = request.get_json() or {}
            user_dto = UserRegistrationDTO.from_dict(json_data)
            created_user = _core_service.register_user(user_dto)
            return (
                jsonify({
                    "status": "success",
                    "message": f"Usuario '{created_user.username}' registrado exitosamente",
                    "redirect_url": url_for("core.index_view"),
                }),
                201,
            )
        except ValueError as validation_error:
            return (
                jsonify({
                    "status": "bad request",
                    "message": str(validation_error),
                }),
                400,
            )
        except UserAlreadyExistsError as conflict_error:
            return (
                jsonify({
                    "status": "conflict",
                    "message": str(conflict_error),
                }),
                409,
            )


class LoginHandler(MethodView):
    def get(self):
        return render_template("auth/login.html")

    def post(self):
        try:
            json_data = request.get_json() or {}
            login_dto = LoginDTO.from_dict(json_data)
            _ = _core_service.authenticate_user(login_dto)

            return (
                jsonify({
                    "status": "success",
                    "message": "Usuario autenticado exitosamente",
                }),
                200,
            )
        except ValueError as validation_error:
            return (
                jsonify({
                    "status": "bad request",
                    "message": str(validation_error),
                }),
                400,
            )
        except InvalidCredentialsError as auth_error:
            return (
                jsonify({
                    "status": "unauthorized",
                    "message": str(auth_error),
                }),
                401,
            )


class LogoutHandler(MethodView):
    def post(self):
        _core_service.logout_user()
        return redirect(url_for("core.login_view"))


class VisitorLogHandler(MethodView):
    def post(self):
        try:
            json_data = request.get_json() or {}
            visitor_dto = VisitorLogDTO.from_dict(json_data)
            log = _core_service.log_visitor(visitor_dto)
            return (
                jsonify({
                    "status": "success",
                    "message": "Entrada de visitante registrada exitosamente",
                    "log_id": log.id,
                }),
                201,
            )
        except ValueError as validation_error:
            return (
                jsonify({
                    "status": "bad request",
                    "message": str(validation_error),
                }),
                400,
            )
        except VisitorLogCreationError as creation_error:
            return (
                jsonify({
                    "status": "internal error",
                    "message": str(creation_error),
                }),
                500,
            )


class VisitorStatsHandler(MethodView):
    def get(self):
        if g.user_role != "ADMIN":
            return redirect(url_for("core.index_view"))
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        interval = request.args.get("interval", "day")
        analytics = _core_service.get_visitor_analytics(start_date, end_date, interval)
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(analytics)
        return render_template("core/visitor_stats.html", data=analytics)


core_bp.add_url_rule("/", view_func=IndexHandler.as_view("index_view"))
core_bp.add_url_rule(
    "/register", view_func=RegistrationHandler.as_view("register_view")
)
core_bp.add_url_rule("/login", view_func=LoginHandler.as_view("login_view"))
core_bp.add_url_rule("/logout", view_func=LogoutHandler.as_view("logout_view"))
core_bp.add_url_rule(
    "/visitor-log", view_func=VisitorLogHandler.as_view("visitor_log_view")
)
core_bp.add_url_rule(
    "/admin/stats/visitors", view_func=VisitorStatsHandler.as_view("visitor_stats_view")
)
