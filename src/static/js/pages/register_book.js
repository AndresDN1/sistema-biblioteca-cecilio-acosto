document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("register-book-form");
    const feedbackBox = document.getElementById("form-feedback");

    if (!form) return;

    const showFeedback = (message, isSuccess = true) => {
        if (!feedbackBox) return;
        feedbackBox.textContent = message;
        feedbackBox.className = `alert ${isSuccess ? 'alert-success' : 'alert-danger'} margin-top-sm`;
        feedbackBox.classList.remove("hidden");
        feedbackBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    };

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        if (feedbackBox) feedbackBox.classList.add("hidden");

        const getValue = (id) => {
            const el = document.getElementById(id);
            return el ? el.value.trim() : "";
        };

        const yearVal = getValue("publication_year");
        const collectionVal = getValue("collection_id");

        const payload = {
            title: getValue("title"),
            author: getValue("author"),
            publisher: getValue("publisher"),
            isbn: getValue("isbn") || null,
            publication_year: yearVal !== "" ? parseInt(yearVal, 10) : null,
            dewey_code: getValue("dewey_code") || null,
            collection_id: collectionVal !== "" ? parseInt(collectionVal, 10) : 1,
            is_braille: document.getElementById("is_braille")?.checked || false,
            is_audiobook: document.getElementById("is_audiobook")?.checked || false,
            classification_system: "DEWEY"
        };

        try {
            const response = await fetch("/inventory/books", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok) {
                showFeedback(data.message || "Error al registrar el libro.", false);
                return;
            }

            showFeedback(data.message || "Libro registrado con éxito.", true);
            form.reset();

        } catch (err) {
            console.error("Error sending request:", err);
            showFeedback("Ocurrió un error inesperado al conectar con el servidor.", false);
        }
    });
});
