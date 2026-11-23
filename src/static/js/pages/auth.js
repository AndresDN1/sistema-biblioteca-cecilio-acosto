document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");
    const alertBox = document.getElementById("global-alert");

    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const payload = {
                username: loginForm.username.value.trim(),
                password: loginForm.password.value.trim()
            };

            try {
                const response = await fetch("/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (response.ok) {
                    showAlert("Inicio de sesión exitoso. Redirigiendo...", "success");
                    setTimeout(() => window.location.href = "/", 1000);
                } else {
                    showAlert(data.message || "Credenciales inválidas.", "error");
                }
            } catch (err) {
                showAlert("Error al conectar con el servidor.", "error");
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const payload = {
                full_name: registerForm.full_name.value.trim(),
                username: registerForm.username.value.trim(),
                password: registerForm.password.value.trim()
            };

            try {
                const response = await fetch("/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (response.ok) {
                    showAlert(data.message || "Registro exitoso.", "success");
                    setTimeout(() => window.location.href = data.redirect_url || "/", 1200);
                } else {
                    showAlert(data.message || "Error al completar el registro.", "error");
                }
            } catch (err) {
                showAlert("Error al conectar con el servidor.", "error");
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
