document.addEventListener("DOMContentLoaded", function () {

    console.log("Auth JS loaded");

    // ===== LOGIN =====
    const loginForm = document.getElementById("loginForm");

    if (loginForm) {
        loginForm.addEventListener("submit", async function (e) {
            e.preventDefault();

            console.log("Login submit");

            const data = {
                email: document.getElementById("email").value,
                password: document.getElementById("password").value
            };

            try {
                const res = await fetch("/auth/login", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify(data)
                });

                const result = await res.json();
                console.log("Login result:", result);

                if (result.token) {
                    alert("Đăng nhập thành công!");
                    window.location.href = "/";
                } else {
                    alert(result.error || "Đăng nhập thất bại");
                }

            } catch (err) {
                console.error("Login error:", err);
                alert("Lỗi kết nối server");
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
                const res = await fetch("/auth/register", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify(data)
                });

                const result = await res.json();
                console.log("Register result:", result);

                if (result.message) {
                    alert("Đăng ký thành công!");
                    window.location.href = "/auth/login-page";
                } else {
                    alert(result.error || "Đăng ký thất bại");
                }

            } catch (err) {
                console.error("Register error:", err);
                alert("Lỗi kết nối server");
            }
        });
    }

}); 