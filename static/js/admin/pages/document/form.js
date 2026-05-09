document.addEventListener("DOMContentLoaded", function() {
    
    const typeBtns = document.querySelectorAll(".type-btn");
    const docTypeInput = document.getElementById("doc-type");
    const universityGroup = document.getElementById("group-university");
    const journalGroup = document.getElementById("group-journal");
    const publisherGroup = document.getElementById("group-publisher");
    const submitBtnText = document.getElementById("submit-text");

    // =========================
    // 1. TYPE SWITCHING
    // =========================
    typeBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const type = btn.dataset.type; // book, article, thesis
            
            // UI Active State
            typeBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            // Update Hidden Input
            docTypeInput.value = type.charAt(0).toUpperCase() + type.slice(1);
            submitBtnText.textContent = `Lưu ${docTypeInput.value}`;

            // Toggle Groups
            if (type === "article") {
                if (journalGroup) journalGroup.classList.remove("hidden");
                if (publisherGroup) publisherGroup.classList.add("hidden");
                if (universityGroup) universityGroup.classList.add("hidden");
            } else if (type === "book") {
                if (journalGroup) journalGroup.classList.add("hidden");
                if (publisherGroup) publisherGroup.classList.remove("hidden");
                if (universityGroup) universityGroup.classList.add("hidden");
            } else if (type === "thesis") {
                if (journalGroup) journalGroup.classList.add("hidden");
                if (publisherGroup) publisherGroup.classList.add("hidden");
                if (universityGroup) universityGroup.classList.remove("hidden");
            }
        });
    });

    // =========================
    // 2. DYNAMIC ROWS (AUTHORS & INSTITUTIONS)
    // =========================
    const setupDynamicRow = (containerId, addBtnId, rowClass, html) => {
        const container = document.getElementById(containerId);
        const addBtn = document.getElementById(addBtnId);

        if (!addBtn) return;

        addBtn.addEventListener("click", () => {
            const row = document.createElement("div");
            row.className = `dynamic-row ${rowClass}`;
            row.style.display = "grid";
            row.style.gridTemplateColumns = "2fr 1fr 40px";
            row.style.gap = "10px";
            row.style.marginBottom = "10px";
            row.style.alignItems = "end";
            row.innerHTML = html;
            container.appendChild(row);

            row.querySelector(".remove-row-btn").addEventListener("click", () => row.remove());
        });
    };

    // Authors
    setupDynamicRow(
        "author-list", 
        "add-author-btn", 
        "author-row", 
        `
            <div class="form-group">
                <input type="text" class="auth-name" placeholder="Tên tác giả" list="author-datalist">
            </div>
            <div class="form-group">
                <select class="auth-role">
                    <option value="author">Tác giả chính</option>
                    <option value="contributor">Đồng tác giả</option>
                    <option value="supervisor">Giảng viên hướng dẫn</option>
                </select>
            </div>
            <div class="remove-row-btn"><i class="fas fa-trash"></i></div>
        `
    );

    // Institutions
    setupDynamicRow(
        "inst-list", 
        "add-inst-btn", 
        "inst-row", 
        `
            <div class="form-group">
                <input type="text" class="inst-name" placeholder="Tên cơ quan hoặc trường học" list="institution-datalist">
            </div>
            <div class="form-group">
                <select class="inst-role">
                    <option value="publisher">Nhà xuất bản</option>
                    <option value="university">Trường đại học</option>
                    <option value="research_center">Viện nghiên cứu</option>
                    <option value="other">Khác</option>
                </select>
            </div>
            <div class="remove-row-btn"><i class="fas fa-trash"></i></div>
        `
    );

    // Listen for existing remove buttons (for Edit page)
    document.querySelectorAll(".remove-row-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.target.closest(".dynamic-row").remove();
        });
    });

    // =========================
    // 3. IMAGE PREVIEW
    // =========================
    const imageInput = document.getElementById("image-input");
    const imagePreview = document.getElementById("image-preview");

    if (imageInput) {
        imageInput.addEventListener("change", function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = "block";
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // =========================
    // 4. FORM SUBMIT (JSON PREP)
    // =========================
    const mainForm = document.getElementById("main-doc-form");
    
    mainForm.addEventListener("submit", function(e) {
        // Collect Authors
        const authorData = [];
        document.querySelectorAll(".author-row").forEach(row => {
            const name = row.querySelector(".auth-name").value;
            const role = row.querySelector(".auth-role").value;
            if (name) {
                authorData.push({ name, role });
            }
        });
        document.getElementById("authors-json-hidden").value = JSON.stringify(authorData);

        // Collect Institutions
        const instData = [];
        document.querySelectorAll(".inst-row").forEach(row => {
            const name = row.querySelector(".inst-name").value;
            const role = row.querySelector(".inst-role").value;
            if (name) {
                instData.push({ name, role });
            }
        });
        document.getElementById("institutions-json-hidden").value = JSON.stringify(instData);

        // Collect Multi-selects
        const getList = (id) => {
            const val = document.getElementById(id).value;
            return val ? val.split(",").map(s => s.trim()).filter(s => s) : [];
        };

        document.getElementById("subjects-hidden").value = JSON.stringify(getList("subjects-input"));
        document.getElementById("keywords-hidden").value = JSON.stringify(getList("keywords-input"));
        document.getElementById("categories-hidden").value = JSON.stringify(getList("categories-input"));
        document.getElementById("languages-hidden").value = JSON.stringify(getList("languages-input"));
    });
});