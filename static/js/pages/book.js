document.querySelectorAll(".book-item").forEach(item => {
    item.addEventListener("click", function (e) {

        if (!e.target.closest("a")) {
            let link = item.querySelector("a");
            if (link) window.location = link.href;
        }

    });
});