let ALL_ROWS = [];   // keep original copy

async function loadSolveSteps() {
    const rows = await fetch("/analytics/steps").then(r => r.json());
    ALL_ROWS = rows;
    renderRows(rows);
}

// render function
function renderRows(rows) {
    let html = "";
    rows.forEach(s => {
        html += `<tr>
            <td>${s.id}</td>
            <td>${s.puzzle}</td>
            <td>${s.session_id}</td>
            <td>${s.step_number}</td>
            <td>${s.hint_text || ""}</td>
            <td>${s.r}</td>
            <td>${s.c}</td>
            <td>${s.value}</td>
            <td>${s.method_used || ""}</td>
            <td>${s.created_at}</td>
        </tr>`;
    });
    document.getElementById("steps-body").innerHTML = html;
}

// filter function
document.getElementById("search-input").addEventListener("input", function () {
    const q = this.value.trim().toLowerCase();

    if (!q) {
        renderRows(ALL_ROWS);
        return;
    }

    const filtered = ALL_ROWS.filter(s =>
        String(s.session_id).toLowerCase().includes(q)
    );

    renderRows(filtered);
});

loadSolveSteps();