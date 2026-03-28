document.querySelector(".admin-form").addEventListener("submit", function(e) {
    const title = document.querySelector("input[name='title']").value;

    if (!title.trim()) {
        alert("Tiêu đề không được để trống!");
        e.preventDefault();
    }
});