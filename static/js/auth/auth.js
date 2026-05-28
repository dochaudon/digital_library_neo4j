document.addEventListener("DOMContentLoaded", function () {

    console.log("Auth JS loaded");

    // ===== LOGIN =====
    const loginForm = document.getElementById("loginForm");

    if (loginForm) {
        loginForm.addEventListener("submit", async function (e) {
            e.preventDefault();

            const submitBtn = loginForm.querySelector("button[type='submit']");
            const originalText = submitBtn.innerText;
            submitBtn.disabled = true;
            submitBtn.innerText = "Đang đăng nhập...";

            const data = {
                email: document.getElementById("email").value,
                password: document.getElementById("password").value
            };

            try {
                const res = await fetch("/auth/api/login", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify(data)
                });

                const result = await res.json();

                if (result.token) {
                    window.location.href = "/";
                } else {
                    alert(result.error || "Đăng nhập thất bại");
                    submitBtn.disabled = false;
                    submitBtn.innerText = originalText;
                }

            } catch (err) {
                console.error("Login error:", err);
                alert("Lỗi kết nối server");
                submitBtn.disabled = false;
                submitBtn.innerText = originalText;
            }
        });
    }


    // ===== REGISTER =====
    const registerForm = document.getElementById("registerForm");

    if (registerForm) {
        registerForm.addEventListener("submit", async function (e) {
            e.preventDefault();

            console.log("Register submit");

            const password = document.getElementById("password").value;
            const confirmPassword = document.getElementById("confirmPassword").value;

            if (password !== confirmPassword) {
                alert("Mật khẩu không khớp!");
                return;
            }

            const data = {
                username: document.getElementById("username").value,
                email: document.getElementById("email").value,
                password: password
            };

            try {
                const res = await fetch("/auth/api/register", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify(data)
                });

                const result = await res.json();
                console.log("Register result:", result);

                if (result.message) {
                    alert("Đăng ký thành công!");
                    window.location.href = "/auth/login";
                } else {
                    alert(result.error || "Đăng ký thất bại");
                }

            } catch (err) {
                console.error("Register error:", err);
                alert("Lỗi kết nối server");
            }

        });
    }

    // ===== TOGGLE PASSWORD VISIBILITY =====
    document.querySelectorAll(".toggle-password").forEach(icon => {
        icon.addEventListener("click", function () {
            const input = this.parentNode.querySelector("input");
            if (input.type === "password") {
                input.type = "text";
                this.classList.remove("fa-eye");
                this.classList.add("fa-eye-slash");
            } else {
                input.type = "password";
                this.classList.remove("fa-eye-slash");
                this.classList.add("fa-eye");
            }
        });
    });

}); 