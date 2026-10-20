const temperatureForm = document.getElementById("temperatureForm");

document.querySelectorAll(".quick").forEach(button => {
    button.addEventListener("click", () => {
        document.getElementById("temperature").value = button.dataset.value;
    });
});

const tableSearch = document.getElementById("tableSearch");
if (tableSearch) {
    tableSearch.addEventListener("input", () => {
        const query = tableSearch.value.toLowerCase();
        const rows = document.querySelectorAll("#tableContainer tbody tr");
        let visible = 0;

        rows.forEach(row => {
            const match = row.textContent.toLowerCase().includes(query);
            row.style.display = match ? "" : "none";
            if (match) visible++;
        });

        document.getElementById("rowCount").textContent =
            `Showing ${visible} of ${rows.length} preview rows`;
    });

    const rows = document.querySelectorAll("#tableContainer tbody tr");
    document.getElementById("rowCount").textContent =
        `Showing ${rows.length} preview rows`;
}

if (temperatureForm) {
    temperatureForm.addEventListener("submit", () => {
        const button = temperatureForm.querySelector("button[type='submit']");
        button.textContent = "Analyzing...";
    });
}
