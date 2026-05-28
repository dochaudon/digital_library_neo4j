document.addEventListener("DOMContentLoaded", function () {

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
            const typeMap = {
                book: "Sách",
                article: "Bài báo",
                thesis: "Luận văn"
            };
            submitBtnText.textContent = `Lưu ${typeMap[type] || docTypeInput.value}`;

            // Toggle Groups
            if (type === "article") {
                if (journalGroup) journalGroup.classList.remove("hidden");
                if (publisherGroup) publisherGroup.classList.remove("hidden");
                if (universityGroup) universityGroup.classList.remove("hidden");
            } else if (type === "book") {
                if (journalGroup) journalGroup.classList.add("hidden");
                if (publisherGroup) publisherGroup.classList.remove("hidden");
                if (universityGroup) universityGroup.classList.remove("hidden");
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

    // Universities
    setupDynamicRow(
        "university-list",
        "add-university-btn",
        "university-row",
        `
            <div class="form-group">
                <input type="text" class="uni-name" placeholder="Tên trường đại học" list="university-datalist">
            </div>
            <div class="form-group">
                <input type="text" class="uni-role" value="university" readonly class="readonly">
            </div>
            <div class="remove-row-btn"><i class="fas fa-trash"></i></div>
        `
    );

    // Publishers
    setupDynamicRow(
        "publisher-list",
        "add-publisher-btn",
        "publisher-row",
        `
            <div class="form-group">
                <input type="text" class="pub-name" placeholder="Tên cơ quan hoặc NXB" list="publisher-datalist">
            </div>
            <div class="form-group">
                <input type="text" class="pub-role" value="publisher" readonly class="readonly">
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
    // 3. IMAGE & FILE PREVIEW
    // =========================
    const imageInput = document.getElementById("image-input");
    const imagePreview = document.getElementById("image-preview");

    if (imageInput) {
        imageInput.addEventListener("change", function () {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = "block";
                }
                reader.readAsDataURL(file);
            }
        });
    }

    const fileInput = document.getElementById("file-input");
    const fileInfo = document.getElementById("file-info");

    if (fileInput && fileInfo) {
        fileInput.addEventListener("change", function () {
            const file = this.files[0];
            if (file) {
                const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
                fileInfo.innerHTML = `
                    <div style="display: inline-flex; align-items: center; background-color: #d1fae5; color: #065f46; padding: 6px 12px; border-radius: 6px; border: 1px solid #a7f3d0; margin-top: 8px; gap: 6px; font-weight: 500;">
                        <i class="fas fa-check-circle" style="color: #10b981;"></i>
                        <span>Đã chọn: <strong>${file.name}</strong> (${sizeMB} MB)</span>
                    </div>
                `;
            }
        });
    }

    // =========================
    // 4. FORM SUBMIT (JSON PREP)
    // =========================
    const mainForm = document.getElementById("main-doc-form");

    mainForm.addEventListener("submit", function (e) {
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

        // Collect Institutions (Universities + Publishers)
        const instData = [];

        // Universities
        document.querySelectorAll(".university-row").forEach(row => {
            const name = row.querySelector(".uni-name").value;
            const role = "university";
            if (name) {
                instData.push({ name, role });
            }
        });

        // Publishers
        document.querySelectorAll(".publisher-row").forEach(row => {
            const name = row.querySelector(".pub-name").value;
            const role = "publisher";
            if (name) {
                instData.push({ name, role });
            }
        });

        const catVal = document.getElementById("categories-input").value.trim();
        document.getElementById("categories-hidden").value = JSON.stringify(catVal ? [catVal] : []);

        const langVal = document.getElementById("languages-input").value.trim();
        document.getElementById("languages-hidden").value = JSON.stringify(langVal ? [langVal] : []);

        document.getElementById("institutions-json-hidden").value = JSON.stringify(instData);
    });

    // =====================================================
    // 4.5. GENERIC DYNAMIC TAG INPUTS FOR METADATA
    // =====================================================
    function setupTagInput(inputId, hiddenId, containerId, datalistId) {
        const input = document.getElementById(inputId);
        const hidden = document.getElementById(hiddenId);
        const container = document.getElementById(containerId);
        if (!input || !hidden || !container) return;

        let tags = [];

        // Initialize tags if hidden input already has values (for Edit page)
        if (hidden.value) {
            try {
                tags = JSON.parse(hidden.value);
            } catch (e) {
                tags = hidden.value.split(",").map(s => s.trim()).filter(s => s);
            }
        }

        const renderTags = () => {
            container.innerHTML = "";
            tags.forEach((tagText, index) => {
                const tag = document.createElement("div");
                tag.className = "relation-tag";
                tag.style.cssText = "display: inline-flex; align-items: center; background-color: #e0e7ff; border: 1px solid #c7d2fe; border-radius: 20px; padding: 4px 10px; font-size: 13px; color: #3730a3; gap: 6px; font-weight: 500; margin-right: 6px; margin-bottom: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);";

                const text = document.createElement("span");
                text.textContent = tagText;

                const removeBtn = document.createElement("i");
                removeBtn.className = "fas fa-times-circle";
                removeBtn.style.cssText = "color: #f87171; cursor: pointer; font-size: 13px; transition: color 0.2s;";
                removeBtn.addEventListener("mouseover", () => removeBtn.style.color = "#ef4444");
                removeBtn.addEventListener("mouseout", () => removeBtn.style.color = "#f87171");
                removeBtn.addEventListener("click", () => {
                    tags.splice(index, 1);
                    renderTags();
                });

                tag.appendChild(text);
                tag.appendChild(removeBtn);
                container.appendChild(tag);
            });
            hidden.value = JSON.stringify(tags);
        };

        const addTag = (val) => {
            val = val.trim();
            // Remove trailing commas if any
            if (val.endsWith(",")) {
                val = val.slice(0, -1).trim();
            }
            if (val && !tags.includes(val)) {
                tags.push(val);
                renderTags();
            }
            input.value = "";
        };

        // Listen for enter or comma
        input.addEventListener("keydown", function (e) {
            if (e.key === "Enter" || e.key === ",") {
                e.preventDefault();
                addTag(this.value);
            }
        });

        // Listen for autocomplete selection from datalist
        const datalist = document.getElementById(datalistId);
        if (datalist) {
            // Keep track of datalist options
            input.addEventListener("input", function (e) {
                const val = this.value.trim();
                const options = Array.from(datalist.options).map(opt => opt.value);
                if (options.includes(val)) {
                    addTag(val);
                }
            });
        }

        // Also add tag when input loses focus (blur)
        input.addEventListener("blur", function () {
            addTag(this.value);
        });

        renderTags();
    }

    setupTagInput("subjects-input", "subjects-hidden", "subjects-tags", "subject-datalist");
    setupTagInput("keywords-input", "keywords-hidden", "keywords-tags", "keyword-datalist");

    // =====================================================
    // 5. RELATED DOCUMENTS AUTOCOMPLETE & DYNAMIC TAGS (NEW)
    // =====================================================
    const searchInput = document.getElementById("related-docs-search");
    const suggestionsBox = document.getElementById("related-docs-suggestions");
    const tagsContainer = document.getElementById("related-docs-tags");
    const hiddenRelatedInput = document.getElementById("related-docs-hidden");

    if (searchInput && suggestionsBox && tagsContainer) {
        const selectedDocIds = new Set();
        const selectedDocsList = [];

        // Hộp vẽ thẻ Tag động
        const renderTags = () => {
            tagsContainer.innerHTML = "";
            selectedDocsList.forEach(doc => {
                const tag = document.createElement("div");
                tag.className = "relation-tag";
                tag.style.cssText = "display: inline-flex; align-items: center; background-color: #e0e7ff; border: 1px solid #c7d2fe; border-radius: 20px; padding: 6px 14px; font-size: 13px; color: #3730a3; gap: 8px; font-weight: 600; box-shadow: 0 1px 2px rgba(0,0,0,0.05); transition: all 0.2s ease;";

                const titleText = document.createElement("span");
                titleText.textContent = `[${doc.id}] ${doc.title}`;
                titleText.style.maxWidth = "350px";
                titleText.style.overflow = "hidden";
                titleText.style.textOverflow = "ellipsis";
                titleText.style.whiteSpace = "nowrap";

                const removeBtn = document.createElement("i");
                removeBtn.className = "fas fa-times-circle";
                removeBtn.style.cssText = "color: #f87171; cursor: pointer; font-size: 14px; transition: color 0.2s;";
                removeBtn.addEventListener("mouseover", () => removeBtn.style.color = "#ef4444");
                removeBtn.addEventListener("mouseout", () => removeBtn.style.color = "#f87171");

                removeBtn.addEventListener("click", () => {
                    selectedDocIds.delete(doc.id);
                    const idx = selectedDocsList.findIndex(d => d.id === doc.id);
                    if (idx > -1) selectedDocsList.splice(idx, 1);
                    renderTags();
                });

                tag.appendChild(titleText);
                tag.appendChild(removeBtn);
                tagsContainer.appendChild(tag);
            });

            // Tự động đồng bộ hóa vào trường ẩn để submit
            if (hiddenRelatedInput) {
                hiddenRelatedInput.value = JSON.stringify(Array.from(selectedDocIds));
            }
        };

        // Nạp các tài liệu đã liên quan trước đó (khi sửa)
        if (window.initialRelatedDocs && window.initialRelatedDocs.length > 0) {
            window.initialRelatedDocs.forEach(doc => {
                if (!selectedDocIds.has(doc.id)) {
                    selectedDocIds.add(doc.id);
                    selectedDocsList.push(doc);
                }
            });
        }
        renderTags();

        // Bắt sự kiện gõ tìm kiếm tự động lọc
        searchInput.addEventListener("input", function () {
            const query = this.value.trim().toLowerCase();
            suggestionsBox.innerHTML = "";

            if (!query) {
                suggestionsBox.style.display = "none";
                return;
            }

            // Lọc danh sách (không chứa phần tử đã chọn, và tìm theo ID hoặc tên tài liệu)
            const matches = (window.allDocuments || []).filter(doc => {
                return !selectedDocIds.has(doc.id) &&
                    (doc.id.toLowerCase().includes(query) || doc.title.toLowerCase().includes(query));
            });

            if (matches.length === 0) {
                const noResult = document.createElement("div");
                noResult.textContent = "Không tìm thấy tài liệu phù hợp";
                noResult.style.cssText = "padding: 10px 14px; color: #94a3b8; font-size: 13px; text-align: center;";
                suggestionsBox.appendChild(noResult);
            } else {
                // Hiển thị tối đa 8 kết quả phù hợp nhất
                matches.slice(0, 8).forEach(doc => {
                    const item = document.createElement("div");
                    item.className = "suggestion-item";
                    item.style.cssText = "padding: 10px 14px; cursor: pointer; font-size: 13px; color: #334155; border-bottom: 1px solid #f1f5f9; transition: background-color 0.2s;";
                    item.innerHTML = `<strong style="color: #4f46e5;">[${doc.id}]</strong> ${doc.title}`;

                    item.addEventListener("mouseover", () => item.style.backgroundColor = "#f5f3ff");
                    item.addEventListener("mouseout", () => item.style.backgroundColor = "transparent");

                    item.addEventListener("click", () => {
                        selectedDocIds.add(doc.id);
                        selectedDocsList.push(doc);
                        renderTags();
                        searchInput.value = "";
                        suggestionsBox.style.display = "none";
                    });

                    suggestionsBox.appendChild(item);
                });
            }

            suggestionsBox.style.display = "block";
        });

        // Ẩn bảng gợi ý khi bấm ra ngoài
        document.addEventListener("click", function (e) {
            if (!suggestionsBox.contains(e.target) && e.target !== searchInput) {
                suggestionsBox.style.display = "none";
            }
        });
    }
});