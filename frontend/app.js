const API_BASE = "https://sgsbaban-ai-task-manager-gwftgffyh7a0g8gz.ukwest-01.azurewebsites.net";
const tasksDiv = document.getElementById("tasks");
const fetchStatus = document.getElementById("fetch-status");

// ── Load & display all tasks ──────────────────────────────────────────────────
async function loadTasks() {
    tasksDiv.innerHTML = `<p class="loading">Loading tasks…</p>`;
    try {
        const response = await fetch(`${API_BASE}/tasks`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        renderTasks(data);
    } catch (err) {
        tasksDiv.innerHTML = `<p class="error">Error fetching tasks: ${err.message}</p>`;
        console.error(err);
    }
}

function renderTasks(tasks) {
    tasksDiv.innerHTML = "";

    if (tasks.length === 0) {
        tasksDiv.innerHTML = `
            <div class="empty-state">
                <p>No tasks yet.</p>
                <p>Enter a GitHub username &amp; repo above and click <strong>Fetch &amp; Analyse</strong>.</p>
            </div>`;
        return;
    }

    tasks.forEach(task => {
        const isDone = task.status === "done";
        const div = document.createElement("div");
        div.className = `task ${isDone ? "task-done" : ""}`;
        div.innerHTML = `
            <div class="task-meta">
                <span class="badge">#${task.id}</span>
                <span class="repo-name">${task.repo}</span>
                <span class="status-badge status-${task.status}">${task.status}</span>
            </div>
            <p class="task-content">${task.content.replace(/\n/g, "<br>")}</p>
            ${!isDone
                ? `<button onclick="markDone(${task.id})">Mark as Done</button>`
                : `<span class="done-label">✔ Completed</span>`
            }
        `;
        tasksDiv.appendChild(div);
    });
}

// ── Fetch & analyse a GitHub repo ────────────────────────────────────────────
async function fetchTasks() {
    const username = document.getElementById("username").value.trim();
    const repo     = document.getElementById("repo").value.trim();
    const btn      = document.getElementById("fetch-btn");

    if (!username || !repo) {
        fetchStatus.innerHTML = `<p class="error">Please enter both a username and a repo name.</p>`;
        return;
    }

    btn.disabled = true;
    btn.textContent = "Fetching…";
    fetchStatus.innerHTML = `<p class="loading">Contacting GitHub and running AI analysis…</p>`;

    try {
        const response = await fetch(`${API_BASE}/process-task`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, repo })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || `HTTP ${response.status}`);
        }

        const result = await response.json();
        fetchStatus.innerHTML = `
            <p class="success">
                Processed <strong>${result.issues_processed}</strong> issues —
                <strong>${result.new_tasks_created}</strong> new task(s) created.
            </p>`;
        loadTasks();
    } catch (err) {
        fetchStatus.innerHTML = `<p class="error">${err.message}</p>`;
        console.error(err);
    } finally {
        btn.disabled = false;
        btn.textContent = "Fetch & Analyse";
    }
}

// ── Mark task as done ─────────────────────────────────────────────────────────
async function markDone(taskId) {
    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}?new_status=done`, {
            method: "PATCH"
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        loadTasks();
    } catch (err) {
        console.error("Failed to update task:", err);
    }
}

// ── Init ──────────────────────────────────────────────────────────────────────
loadTasks();
