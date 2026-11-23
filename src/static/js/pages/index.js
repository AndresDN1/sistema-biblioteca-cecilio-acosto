document.addEventListener("DOMContentLoaded", () => {
    const track = document.getElementById("carouselTrack");
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");

    if (track && prevBtn && nextBtn) {
        let scrollAmount = 0;
        const step = 250;

        nextBtn.addEventListener("click", () => {
            const maxScroll = track.scrollWidth - track.parentElement.clientWidth;
            if (scrollAmount < maxScroll) {
                scrollAmount = Math.min(scrollAmount + step, maxScroll);
                track.style.transform = `translateX(-${scrollAmount}px)`;
            }
        });

        prevBtn.addEventListener("click", () => {
            if (scrollAmount > 0) {
                scrollAmount = Math.max(scrollAmount - step, 0);
                track.style.transform = `translateX(-${scrollAmount}px)`;
            }
        });
    }

    const visitorForm = document.getElementById("visitorForm");
    const alertBox = document.getElementById("global-alert");

    if (visitorForm) {
        visitorForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const payload = {
                visitor_id: document.getElementById("visitor_id").value.trim(),
                visitor_name: document.getElementById("visitor_name").value.trim(),
                contact_info: document.getElementById("contact_info").value.trim()
            };

            try {
                const response = await fetch("/visitor-log", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (response.ok) {
                    showAlert(data.message || "Visitante registrado exitosamente.", "success");
                    visitorForm.reset();
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    showAlert(data.message || "No se pudo registrar al visitante.", "error");
                }
            } catch (err) {
                showAlert("Error de conexión con el servidor.", "error");
            }
        });
    }

    function showAlert(msg, type) {
        if (!alertBox) return;
        alertBox.textContent = msg;
        alertBox.className = `alert alert-${type}`;
        alertBox.style.display = "block";
    }
});
