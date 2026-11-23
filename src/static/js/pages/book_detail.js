document.addEventListener("DOMContentLoaded", () => {
    const feedbackBox = document.getElementById("detail-feedback");
    const favoriteBtn = document.getElementById("btn-favorite");
    const copyForm = document.getElementById("add-copy-form");
    const editForm = document.getElementById("edit-book-form");
    const deleteBookBtn = document.getElementById("btn-delete-book");
    const itemsList = document.getElementById("items-list");

    const showFeedback = (message, isSuccess = true) => {
        if (!feedbackBox) return;
        feedbackBox.textContent = message;
        feedbackBox.className = `alert ${isSuccess ? 'alert-success' : 'alert-danger'} margin-top-sm`;
        feedbackBox.classList.remove("hidden");
        feedbackBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    };

    if (favoriteBtn) {
        favoriteBtn.addEventListener("click", async () => {
            const bookId = favoriteBtn.getAttribute("data-book-id");
            const isFavoriteCurrently = favoriteBtn.getAttribute("data-is-favorite") === "true";

            const method = isFavoriteCurrently ? "DELETE" : "POST";
            const endpoint = `/inventory/books/${bookId}/interest`;

            try {
                favoriteBtn.disabled = true;

                const response = await fetch(endpoint, {
                    method: method,
                    headers: {
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    }
                });

                const data = await response.json().catch(() => ({}));

                if (response.status === 401) {
                    showFeedback("Debe iniciar sesión para guardar libros en sus favoritos.", false);
                    return;
                }

                if (!response.ok) {
                    showFeedback(data.message || "No se pudo actualizar el estado de favorito.", false);
                    return;
                }

                const newFavoriteState = typeof data.is_interested !== "undefined"
                    ? data.is_interested
                    : !isFavoriteCurrently;

                favoriteBtn.setAttribute("data-is-favorite", newFavoriteState ? "true" : "false");

                if (newFavoriteState) {
                    favoriteBtn.className = "btn btn-primary";
                    favoriteBtn.textContent = "★ En Mis Intereses";
                    showFeedback(data.message || "Libro agregado a sus intereses correctamente.", true);
                } else {
                    favoriteBtn.className = "btn btn-outline";
                    favoriteBtn.textContent = "☆ Marcar como Interesado";
                    showFeedback(data.message || "Libro eliminado de sus intereses.", true);
                }

            } catch (err) {
                console.error("Error toggling favorite:", err);
                showFeedback("Error de conexión al procesar la solicitud.", false);
            } finally {
                favoriteBtn.disabled = false;
            }
        });
    }

    if (copyForm) {
        copyForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            if (feedbackBox) feedbackBox.classList.add("hidden");

            const bookId = copyForm.getAttribute("data-book-id");
            const shelfLocationInput = document.getElementById("shelf_location");
            const shelfLocation = shelfLocationInput ? shelfLocationInput.value.trim() : "";

            if (!shelfLocation) {
                showFeedback("Por favor ingrese una ubicación válida en estantería.", false);
                return;
            }

            const payload = {
                shelf_location: shelfLocation,
                is_available: true
            };

            try {
                const response = await fetch(`/inventory/books/${bookId}/items`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    body: JSON.stringify(payload)
                });

                const data = await response.json().catch(() => ({}));

                if (response.status === 403) {
                    showFeedback("No tiene permisos de administrador para realizar esta acción.", false);
                    return;
                }

                if (!response.ok) {
                    showFeedback(data.message || "Error al registrar el ejemplar.", false);
                    return;
                }

                showFeedback(data.message || "Ejemplar registrado con éxito.", true);
                copyForm.reset();

                updateItemsDOM(data.item || { shelf_location: shelfLocation, is_available: true });

            } catch (err) {
                console.error("Error creating copy:", err);
                showFeedback("Ocurrió un error inesperado al conectar con el servidor.", false);
            }
        });
    }

    if (itemsList) {
        itemsList.addEventListener("click", async (e) => {
            if (e.target.classList.contains("delete-item-btn")) {
                const itemId = e.target.getAttribute("data-item-id");

                if (!confirm("¿Está seguro de que desea eliminar este ejemplar físico del inventario?")) {
                    return;
                }

                try {
                    const response = await fetch(`/inventory/items/${itemId}`, {
                        method: "DELETE",
                        headers: { "Accept": "application/json" }
                    });

                    if (response.ok) {
                        const row = document.getElementById(`item-${itemId}`);
                        if (row) row.remove();

                        const countEl = document.getElementById("items-count");
                        if (countEl) {
                            const current = parseInt(countEl.textContent) || 0;
                            countEl.textContent = Math.max(0, current - 1).toString();
                        }
                        showFeedback("Ejemplar eliminado exitosamente.");
                    } else {
                        const data = await response.json().catch(() => ({}));
                        showFeedback(data.message || "No se pudo eliminar el ejemplar.", false);
                    }
                } catch (err) {
                    showFeedback("Error de conexión al intentar eliminar el ejemplar.", false);
                }
            }
        });
    }

    if (editForm) {
        editForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const bookId = editForm.getAttribute("data-book-id");

            const payload = {
                title: document.getElementById("edit_title").value.trim(),
                author: document.getElementById("edit_author").value.trim(),
                publisher: document.getElementById("edit_publisher").value.trim(),
                isbn: document.getElementById("edit_isbn").value.trim() || null,
                publication_year: parseInt(document.getElementById("edit_year").value) || null,
                is_braille: document.getElementById("edit_braille").checked,
                is_audiobook: document.getElementById("edit_audio").checked,
                collection_id: 1,
                classification_system: "DEWEY"
            };

            try {
                const response = await fetch(`/inventory/books/${bookId}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    showFeedback("Información actualizada exitosamente. Recargando página...");
                    setTimeout(() => window.location.reload(), 1200);
                } else {
                    const data = await response.json().catch(() => ({}));
                    showFeedback(data.message || "Error al actualizar el libro.", false);
                }
            } catch (err) {
                showFeedback("Error al conectar con el servidor para actualizar el libro.", false);
            }
        });
    }

    if (deleteBookBtn) {
        deleteBookBtn.addEventListener("click", async () => {
            const bookId = deleteBookBtn.getAttribute("data-book-id");

            const firstConfirm = confirm("⚠️ ¿ESTÁ SEGURO? Se eliminará este libro y TODOS sus ejemplares físicos.");
            if (!firstConfirm) return;

            const secondConfirm = confirm("Esta acción es irreversible. ¿Desea proceder?");
            if (!secondConfirm) return;

            try {
                const response = await fetch(`/inventory/books/${bookId}`, {
                    method: "DELETE",
                    headers: { "Accept": "application/json" }
                });

                if (response.ok) {
                    alert("Libro eliminado permanentemente del catálogo.");
                    window.location.href = "/inventory/search";
                } else {
                    const data = await response.json().catch(() => ({}));
                    showFeedback(data.message || "Error al intentar eliminar el libro.", false);
                }
            } catch (err) {
                showFeedback("Error de conexión al intentar eliminar el libro.", false);
            }
        });
    }

    function updateItemsDOM(newItem) {
        const list = document.getElementById("items-list");
        const noItemsMsg = document.getElementById("no-items-msg");
        const itemsCount = document.getElementById("items-count");
        const badgeContainer = document.getElementById("availability-badge-container");

        if (noItemsMsg) noItemsMsg.remove();

        if (list) {
            const li = document.createElement("li");
            li.id = `item-${newItem.id || 'new'}`;
            li.className = "item-row";

            const isAdmin = !!document.getElementById("add-copy-form");
            const deleteBtnHtml = isAdmin && newItem.id
                ? `<button class="btn-icon-delete delete-item-btn" data-item-id="${newItem.id}" title="Eliminar ejemplar">×</button>`
                : '';

            li.innerHTML = `
                <span>Ubicación: <strong>${escapeHtml(newItem.shelf_location)}</strong></span>
                <div>
                    <span style="color: var(--success-color); font-weight: bold; margin-right: 1rem;">Disponible</span>
                    ${deleteBtnHtml}
                </div>
            `;
            list.appendChild(li);
        }

        if (itemsCount) {
            const currentCount = parseInt(itemsCount.textContent || "0", 10);
            itemsCount.textContent = (currentCount + 1).toString();
        }

        if (badgeContainer) {
            badgeContainer.innerHTML = `
                <span class="alert alert-success" style="display: inline-block; padding: 0.4rem 0.8rem;">
                    ✔ Disponible
                </span>
                <p class="margin-top-sm">
                    <strong>Ubicación en Estantería:</strong> ${escapeHtml(newItem.shelf_location)}
                </p>
            `;
        }
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
