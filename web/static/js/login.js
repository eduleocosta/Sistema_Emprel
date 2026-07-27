document.addEventListener("DOMContentLoaded", function () {
    var cpfField = document.getElementById("login_cpf");
    var senhaField = document.getElementById("login_senha");
    var btnLogin = document.getElementById("btn_login");
    var erroDiv = document.getElementById("login_error");
    var mostrarSenha = document.getElementById("login_mostrar_senha");

    function somente_digits(value) {
        return (value || "").replace(/\D/g, "");
    }

    function aplicarMascaraCPF(value) {
        var digits = somente_digits(value).slice(0, 11);
        var formatted = "";
        if (digits.length > 0) {
            formatted += digits.slice(0, 3);
        }
        if (digits.length >= 4) {
            formatted += "." + digits.slice(3, 6);
        }
        if (digits.length >= 7) {
            formatted += "." + digits.slice(6, 9);
        }
        if (digits.length >= 10) {
            formatted += "-" + digits.slice(9, 11);
        }
        return formatted;
    }

    function validarCPF(cpf) {
        var digits = somente_digits(cpf);
        if (digits.length !== 11) {
            return false;
        }
        if (/^(\\d)\\1{10}$/.test(digits)) {
            return false;
        }
        for (var i = 9; i < 11; i++) {
            var soma = 0;
            for (var j = 0; j < i; j++) {
                soma += parseInt(digits.charAt(j), 10) * ((i + 1) - j);
            }
            var dig = ((soma * 10) % 11) % 10;
            if (dig !== parseInt(digits.charAt(i), 10)) {
                return false;
            }
        }
        return true;
    }

    function limparErro() {
        if (erroDiv) {
            erroDiv.textContent = "";
            erroDiv.classList.add("d-none");
        }
    }

    function mostrarErro(mensagem) {
        if (erroDiv) {
            erroDiv.textContent = mensagem;
            erroDiv.classList.remove("d-none");
        }
    }

    function tentarLogin() {
        limparErro();
        var cpf = cpfField.value.trim();
        var senha = senhaField.value;

        if (!cpf || !senha) {
            mostrarErro("Preencha CPF e senha.");
            return;
        }

        if (!validarCPF(cpf)) {
            mostrarErro("Informe um CPF válido.");
            return;
        }

        var dados = {
            cpf: cpf,
            senha: senha
        };

        fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dados)
        })
            .then(function (r) { return r.json(); })
            .then(function (result) {
                if (result.status === "ok") {
                    window.location.href = "/home";
                } else {
                    mostrarErro(result.message || "Credenciais inválidas.");
                }
            })
            .catch(function () {
                mostrarErro("Erro ao conectar. Tente novamente.");
            });
    }

    if (mostrarSenha) {
        mostrarSenha.addEventListener("change", function () {
            senhaField.type = this.checked ? "text" : "password";
        });
    }

    btnLogin.addEventListener("click", function () {
        tentarLogin();
    });

    cpfField.addEventListener("input", function () {
        var posicao = this.selectionStart;
        var valorAntes = this.value;
        this.value = aplicarMascaraCPF(this.value);
        if (this.value.length > valorAntes.length && this.value.length >= 14) {
            var diff = this.value.length - valorAntes.length;
            senhaField.focus();
        }
        if (somente_digits(this.value).length >= 11) {
            senhaField.focus();
        }
        limparErro();
    });

    cpfField.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            if (somente_digits(this.value).length >= 11) {
                senhaField.focus();
            } else {
                tentarLogin();
            }
        }
    });

    senhaField.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            tentarLogin();
        }
    });

    cpfField.focus();
});