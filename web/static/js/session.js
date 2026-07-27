(function () {
    var SESSION_API = "/api/session";
    var LOGIN_URL = "/login";
    var HOME_URL = "/home";
    var INATIVIDADE_MS = 15 * 60 * 1000;

    function atualizarNavbar() {
        window.location.reload();
    }

    function redirecionarLogin() {
        window.location.href = LOGIN_URL;
    }

    function requireSession() {
        fetch(SESSION_API, { credentials: "same-origin" })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.logged) {
                    redirecionarLogin();
                }
            })
            .catch(function () {
                redirecionarLogin();
            });
    }

    function resetInatividade() {
        localStorage.setItem("emprel_last_activity", Date.now().toString());
    }

    function verificarInatividade() {
        var last = localStorage.getItem("emprel_last_activity");
        if (!last) {
            resetInatividade();
            return;
        }
        if (Date.now() - parseInt(last, 10) > INATIVIDADE_MS) {
            fetch("/api/logout", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "same-origin",
            }).finally(function () {
                redirecionarLogin();
            });
        }
    }

    ["click", "keydown", "mousemove", "scroll", "touchstart"].forEach(function (evt) {
        window.addEventListener(evt, function () {
            resetInatividade();
        }, { passive: true });
    });

    setInterval(verificarInatividade, 30000);
    resetInatividade();
    requireSession();

    (function attachLogout() {
        var btn = document.getElementById("btn_logout");
        if (!btn) {
            return;
        }
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            fetch("/api/logout", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "same-origin",
            }).finally(function () {
                redirecionarLogin();
            });
        });
    })();
})();
