from flask import (
    Blueprint,
    g,
    jsonify,
    render_template,
    request,
)
from flask.views import MethodView

from src.dao.inventory_dao import (
    PostgresBookDAO,
    PostgresInterestDAO,
    PostgresItemDAO,
)
from src.dtos.inventory_dtos import BookDTO, BookSearchDTO, ItemDTO
from src.exceptions.inventory_exceptions import (
    BookAlreadyExistsError,
    BookNotFoundError,
    ItemNotFoundError,
)
from src.services.inventory_service import InventoryService

inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")

_book_dao = PostgresBookDAO()
_item_dao = PostgresItemDAO()
_interest_dao = PostgresInterestDAO()

_inventory_service = InventoryService(
    book_dao=_book_dao,
    item_dao=_item_dao,
    interest_dao=_interest_dao,
)


class BookRegistrationFormHandler(MethodView):
    def get(self):
        if g.user_role != "ADMIN":
            return render_template("errors/forbidden.html"), 403
        return render_template("inventory/register_book.html")


class BookHandler(MethodView):
    def post(self):
        if g.user_role != "ADMIN":
            return (
                jsonify({"status": "forbidden", "message": "Petición prohibida"}),
                403,
            )

        try:
            json_data = request.get_json() or {}
            book_dto = BookDTO.from_dict(json_data)
            created_book = _inventory_service.create_book(book_dto)
            return (
                jsonify({
                    "status": "success",
                    "message": f"Libro '{created_book.title}' registrado exitosamente",
                    "book_id": created_book.id,
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
        except BookAlreadyExistsError as conflict_error:
            return (
                jsonify({
                    "status": "conflict",
                    "message": str(conflict_error),
                }),
                409,
            )

    def put(self, book_id: int):
        if g.user_role != "ADMIN":
            return (
                jsonify({"status": "forbidden", "message": "Petición prohibida"}),
                403,
            )

        try:
            json_data = request.get_json() or {}
            book_dto = BookDTO.from_dict(json_data)
            updated_book = _inventory_service.update_book(book_id, book_dto)
            return (
                jsonify({
                    "status": "success",
                    "message": f"Libro '{updated_book.title}' actualizado exitosamente",
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
        except BookNotFoundError as not_found:
            return (
                jsonify({"status": "not found", "message": str(not_found)}),
                404,
            )
        except BookAlreadyExistsError as conflict_error:
            return (
                jsonify({
                    "status": "conflict",
                    "message": str(conflict_error),
                }),
                409,
            )

    def delete(self, book_id: int):
        if g.user_role != "ADMIN":
            return (
                jsonify({"status": "forbidden", "message": "Petición prohibida"}),
                403,
            )

        try:
            _inventory_service.delete_book(book_id)
            return (
                jsonify({
                    "status": "success",
                    "message": f"Libro ID {book_id} eliminado exitosamente",
                }),
                200,
            )
        except BookNotFoundError as not_found:
            return (
                jsonify({"status": "not found", "message": str(not_found)}),
                404,
            )


class BookDetailHandler(MethodView):
    def get(self, book_id: int):
        try:
            data = _inventory_service.get_book_details(book_id, g.user_id)
            items = data["items"]
            accessible_items = [i for i in items if i.is_available]
            is_accessible = len(accessible_items) > 0
            primary_shelf_location = (
                accessible_items[0].shelf_location if is_accessible else None
            )

            return render_template(
                "inventory/book_detail.html",
                book=data["book"],
                items=items,
                is_favorite=data["is_interested"],
                is_accessible=is_accessible,
                primary_shelf_location=primary_shelf_location,
            )
        except BookNotFoundError as not_found:
            return render_template("errors/404.html", message=str(not_found)), 404


class BookSearchHandler(MethodView):
    def get(self):
        return render_template("inventory/search.html")


class BookSearchResultsHandler(MethodView):
    def get(self):
        search_dto = BookSearchDTO.from_dict(request.args)
        books = _inventory_service.search_books(search_dto)
        return render_template("inventory/results.html", books=books)


class ItemHandler(MethodView):
    def post(self, book_id: int):
        if g.user_role != "ADMIN":
            return (
                jsonify({"status": "forbidden", "message": "Petición prohibida"}),
                403,
            )

        try:
            json_data = request.get_json() or {}
            item_dto = ItemDTO.from_dict(json_data)
            created_item = _inventory_service.add_item(book_id, item_dto)
            return (
                jsonify({
                    "status": "success",
                    "message": "Ejemplar registrado exitosamente",
                    "item": {
                        "id": created_item.id,
                        "book_id": created_item.book_id,
                        "shelf_location": created_item.shelf_location,
                        "is_available": created_item.is_available,
                    },
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
        except BookNotFoundError as not_found:
            return (
                jsonify({"status": "not found", "message": str(not_found)}),
                404,
            )

    def delete(self, item_id: int):
        if g.user_role != "ADMIN":
            return (
                jsonify({
                    "status": "forbidden",
                    "message": "No tiene permisos para realizar esta acción",
                }),
                403,
            )

        try:
            _inventory_service.remove_item(item_id)
            return (
                jsonify({
                    "status": "success",
                    "message": "Ejemplar eliminado correctamente",
                }),
                200,
            )
        except ItemNotFoundError as not_found:
            return (
                jsonify({"status": "not found", "message": str(not_found)}),
                404,
            )


class InterestHandler(MethodView):
    def post(self, book_id: int):
        if not g.user_id:
            return (
                jsonify({
                    "status": "unauthorized",
                    "message": "Debe iniciar sesión para guardar favoritos.",
                }),
                401,
            )

        try:
            is_interested = _inventory_service.toggle_interest(book_id, g.user_id)
            return (
                jsonify({
                    "status": "success",
                    "is_interested": is_interested,
                    "message": (
                        "Libro agregado a intereses"
                        if is_interested
                        else "Libro removido de intereses"
                    ),
                }),
                200,
            )
        except BookNotFoundError as not_found:
            return (
                jsonify({"status": "not found", "message": str(not_found)}),
                404,
            )

    def delete(self, book_id: int):
        if not g.user_id:
            return (
                jsonify({
                    "status": "unauthorized",
                    "message": "Debe iniciar sesión para eliminar favoritos.",
                }),
                401,
            )

        try:
            _inventory_service.toggle_interest(book_id, g.user_id)
            return (
                jsonify({
                    "status": "success",
                    "is_interested": False,
                    "message": "Libro removido de intereses",
                }),
                200,
            )
        except BookNotFoundError as not_found:
            return (
                jsonify({"status": "not found", "message": str(not_found)}),
                404,
            )


inventory_bp.add_url_rule(
    "/books/new",
    view_func=BookRegistrationFormHandler.as_view("book_registration_form"),
)
inventory_bp.add_url_rule("/books", view_func=BookHandler.as_view("book_handler"))
inventory_bp.add_url_rule(
    "/books/<int:book_id>", view_func=BookHandler.as_view("book_by_id_handler")
)
inventory_bp.add_url_rule(
    "/books/<int:book_id>/detail",
    view_func=BookDetailHandler.as_view("book_view"),
)
inventory_bp.add_url_rule("/search", view_func=BookSearchHandler.as_view("search_view"))
inventory_bp.add_url_rule(
    "/results", view_func=BookSearchResultsHandler.as_view("results_view")
)
inventory_bp.add_url_rule(
    "/books/<int:book_id>/items", view_func=ItemHandler.as_view("item_handler")
)
inventory_bp.add_url_rule(
    "/books/<int:book_id>/interest",
    view_func=InterestHandler.as_view("interest_handler"),
)
inventory_bp.add_url_rule(
    "/items/<int:item_id>", view_func=ItemHandler.as_view("item_delete_handler")
)
