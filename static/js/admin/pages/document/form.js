document.addEventListener("DOMContentLoaded", () => {

    const buttons = document.querySelectorAll(".type-btn");
    const forms = document.querySelectorAll(".doc-form");

    buttons.forEach(btn => {
        btn.addEventListener("click", () => {

            // remove active
            buttons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            // hide all forms
            forms.forEach(f => f.classList.add("hidden"));

            // show selected
            const type = btn.dataset.type;
            document.getElementById(`form-${type}`).classList.remove("hidden");
        });
    });

});