// ============================================================
// GLOBAL VARIABLES
// ============================================================

let productivityChart = null;
let analyticsChart = null;


// ============================================================
// PAGE NAVIGATION
// ============================================================

function showSection(sectionId) {

    document.querySelectorAll(".page-section")
        .forEach(section => {
            section.classList.remove("active-section");
        });

    document
        .getElementById(sectionId)
        .classList.add("active-section");


    document.querySelectorAll(".nav-item")
        .forEach(button => {
            button.classList.remove("active");
        });


    event.currentTarget.classList.add("active");


    if (sectionId === "habits") {
        loadAllHabits();
    }

    if (sectionId === "tasks") {
        loadAllTasks();
    }

    if (sectionId === "analytics") {
        loadAnalytics();
    }

    if (sectionId === "insights") {
        loadAIInsights();
    }
}


// ============================================================
// DATE
// ============================================================

function displayCurrentDate() {

    const element =
        document.getElementById("currentDate");

    const today = new Date();

    element.textContent =
        today.toLocaleDateString(
            "en-IN",
            {
                weekday: "long",
                year: "numeric",
                month: "long",
                day: "numeric"
            }
        );
}


// ============================================================
// DASHBOARD
// ============================================================

async function loadDashboard() {

    try {

        const response =
            await fetch("/api/dashboard");

        const data =
            await response.json();


        document.getElementById("totalHabits")
            .textContent = data.total_habits;


        document.getElementById("completedHabits")
            .textContent = data.completed_habits;


        document.getElementById("productivity")
            .textContent = `${data.productivity}%`;


        document.getElementById("longestStreak")
            .textContent =
            `${data.longest_streak} days`;


        document.getElementById("pendingTasks")
            .textContent =
            data.total_tasks -
            data.completed_tasks;


    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );

    }
}


// ============================================================
// HABITS
// ============================================================

async function loadHabits() {

    const response =
        await fetch("/api/habits");

    return await response.json();
}


async function renderDashboardHabits() {

    const habits =
        await loadHabits();


    const container =
        document.getElementById(
            "dashboardHabits"
        );


    container.innerHTML = "";


    if (habits.length === 0) {

        container.innerHTML = `
            <div class="loading">
                No habits yet.
                Create your first habit!
            </div>
        `;

        return;
    }


    habits.forEach(habit => {

        const element =
            createHabitElement(habit);

        container.appendChild(element);

    });
}


function createHabitElement(habit) {

    const element =
        document.createElement("div");

    element.className =
        "habit-item";


    element.innerHTML = `

        <div class="habit-info">

            <div
                class="habit-check
                ${habit.completed_today
                    ? "completed"
                    : ""}"
                onclick="toggleHabit(${habit.id})"
            >

                ${
                    habit.completed_today
                        ? "✓"
                        : ""
                }

            </div>


            <div>

                <div class="habit-name">
                    ${escapeHTML(habit.name)}
                </div>

                <div class="habit-category">
                    ${escapeHTML(habit.category)}
                    • ${habit.frequency}
                </div>

            </div>

        </div>


        <div class="streak">

            🔥 ${habit.streak}

        </div>

    `;


    return element;
}


async function toggleHabit(id) {

    await fetch(
        `/api/habits/${id}/complete`,
        {
            method: "POST"
        }
    );


    await refreshDashboard();

}


async function loadAllHabits() {

    const habits =
        await loadHabits();


    const container =
        document.getElementById(
            "allHabits"
        );


    container.innerHTML = "";


    habits.forEach(habit => {

        const element =
            createHabitElement(habit);


        const deleteButton =
            document.createElement("button");

        deleteButton.className =
            "primary-btn";

        deleteButton.textContent =
            "Delete";


        deleteButton.style.background =
            "#ef4444";


        deleteButton.onclick =
            () => deleteHabit(habit.id);


        element.appendChild(
            deleteButton
        );


        container.appendChild(
            element
        );

    });

}


async function deleteHabit(id) {

    if (!confirm(
        "Are you sure you want to delete this habit?"
    )) {
        return;
    }


    await fetch(
        `/api/habits/${id}`,
        {
            method: "DELETE"
        }
    );


    await refreshDashboard();

    loadAllHabits();

}


async function createHabit() {

    const name =
        document.getElementById(
            "habitName"
        ).value.trim();


    const category =
        document.getElementById(
            "habitCategory"
        ).value;


    const frequency =
        document.getElementById(
            "habitFrequency"
        ).value;


    if (!name) {

        alert(
            "Please enter a habit name."
        );

        return;
    }


    await fetch(
        "/api/habits",
        {

            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({

                name,
                category,
                frequency

            })

        }
    );


    document.getElementById(
        "habitName"
    ).value = "";


    closeHabitModal();


    await refreshDashboard();

}


// ============================================================
// TASKS
// ============================================================

async function loadTasks() {

    const response =
        await fetch("/api/tasks");

    return await response.json();
}


async function loadAllTasks() {

    const tasks =
        await loadTasks();


    const container =
        document.getElementById(
            "allTasks"
        );


    container.innerHTML = "";


    if (tasks.length === 0) {

        container.innerHTML = `
            <div class="loading">
                No tasks available.
            </div>
        `;

        return;
    }


    tasks.forEach(task => {

        const element =
            document.createElement("div");


        element.className =
            "task-item";


        element.innerHTML = `

            <div class="task-left">

                <div
                    class="habit-check
                    ${task.completed
                        ? "completed"
                        : ""}"
                    onclick="toggleTask(${task.id})"
                >

                    ${
                        task.completed
                            ? "✓"
                            : ""
                    }

                </div>


                <div>

                    <div class="task-title">

                        ${escapeHTML(
                            task.title
                        )}

                    </div>


                    <div class="task-description">

                        ${escapeHTML(
                            task.description || ""
                        )}

                    </div>

                </div>

            </div>


            <div>

                <span
                    class="priority ${task.priority}"
                >
                    ${task.priority}
                </span>


                <button
                    class="primary-btn"
                    onclick="deleteTask(${task.id})"
                    style="margin-left:8px"
                >
                    Delete
                </button>

            </div>

        `;


        container.appendChild(
            element
        );

    });

}


async function toggleTask(id) {

    await fetch(
        `/api/tasks/${id}/complete`,
        {
            method: "POST"
        }
    );


    await refreshDashboard();

    loadAllTasks();

}


async function deleteTask(id) {

    if (!confirm(
        "Delete this task?"
    )) {
        return;
    }


    await fetch(
        `/api/tasks/${id}`,
        {
            method: "DELETE"
        }
    );


    await refreshDashboard();

    loadAllTasks();

}


async function createTask() {

    const title =
        document.getElementById(
            "taskTitle"
        ).value.trim();


    const description =
        document.getElementById(
            "taskDescription"
        ).value.trim();


    const priority =
        document.getElementById(
            "taskPriority"
        ).value;


    const dueDate =
        document.getElementById(
            "taskDueDate"
        ).value;


    if (!title) {

        alert(
            "Please enter a task title."
        );

        return;
    }


    await fetch(
        "/api/tasks",
        {

            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({

                title,

                description,

                priority,

                due_date: dueDate

            })

        }
    );


    document.getElementById(
        "taskTitle"
    ).value = "";


    document.getElementById(
        "taskDescription"
    ).value = "";


    closeTaskModal();


    await refreshDashboard();

}


// ============================================================
// AI INSIGHTS
// ============================================================

async function loadAIInsights() {

    const response =
        await fetch(
            "/api/ai-insights"
        );


    const data =
        await response.json();


    renderInsights(
        document.getElementById(
            "allInsights"
        ),
        data.insights
    );


    renderInsights(
        document.getElementById(
            "dashboardInsights"
        ),
        data.insights
    );

}


function renderInsights(
    container,
    insights
) {

    if (!container) {
        return;
    }


    container.innerHTML = "";


    insights.forEach(insight => {

        const element =
            document.createElement("div");


        element.className =
            "ai-insight";


        element.innerHTML = `

            <span>🤖</span>

            <span>
                ${escapeHTML(insight)}
            </span>

        `;


        container.appendChild(
            element
        );

    });

}


// ============================================================
// ANALYTICS
// ============================================================

async function loadAnalytics() {

    const response =
        await fetch(
            "/api/analytics"
        );


    const data =
        await response.json();


    const labels =
        data.map(item =>
            item.date.substring(5)
        );


    const habits =
        data.map(item =>
            item.habits
        );


    const tasks =
        data.map(item =>
            item.tasks
        );


    const context =
        document
            .getElementById(
                "analyticsChart"
            )
            .getContext("2d");


    if (analyticsChart) {

        analyticsChart.destroy();

    }


    analyticsChart =
        new Chart(
            context,
            {

                type: "line",

                data: {

                    labels,

                    datasets: [

                        {
                            label:
                                "Completed Habits",

                            data:
                                habits,

                            borderWidth: 3,

                            tension: 0.4

                        },

                        {
                            label:
                                "Completed Tasks",

                            data:
                                tasks,

                            borderWidth: 3,

                            tension: 0.4

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio:
                        false,

                    plugins: {

                        legend: {
                            display: true
                        }

                    },

                    scales: {

                        y: {

                            beginAtZero:
                                true,

                            ticks: {
                                precision: 0
                            }

                        }

                    }

                }

            }
        );

}


// ============================================================
// PRODUCTIVITY CHART
// ============================================================

async function loadProductivityChart() {

    const response =
        await fetch(
            "/api/analytics"
        );


    const data =
        await response.json();


    const labels =
        data.map(item =>
            item.date.substring(5)
        );


    const values =
        data.map(item =>
            item.habits +
            item.tasks
        );


    const context =
        document
            .getElementById(
                "productivityChart"
            )
            .getContext("2d");


    if (productivityChart) {

        productivityChart.destroy();

    }


    productivityChart =
        new Chart(
            context,
            {

                type: "bar",

                data: {

                    labels,

                    datasets: [

                        {

                            label:
                                "Productivity Activity",

                            data:
                                values,

                            borderRadius: 8

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio:
                        false,

                    plugins: {

                        legend: {
                            display: false
                        }

                    },

                    scales: {

                        y: {

                            beginAtZero:
                                true,

                            ticks: {
                                precision: 0
                            }

                        }

                    }

                }

            }
        );

}


// ============================================================
// MODALS
// ============================================================

function openHabitModal() {

    document
        .getElementById("habitModal")
        .classList.add("show");

}


function closeHabitModal() {

    document
        .getElementById("habitModal")
        .classList.remove("show");

}


function openTaskModal() {

    document
        .getElementById("taskModal")
        .classList.add("show");

}


function closeTaskModal() {

    document
        .getElementById("taskModal")
        .classList.remove("show");

}


// ============================================================
// REFRESH
// ============================================================

async function refreshDashboard() {

    await loadDashboard();

    await renderDashboardHabits();

    await loadAIInsights();

    await loadProductivityChart();

}


// ============================================================
// SECURITY HELPER
// ============================================================

function escapeHTML(value) {

    const div =
        document.createElement("div");

    div.textContent =
        value || "";

    return div.innerHTML;

}


// ============================================================
// INITIALIZATION
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        displayCurrentDate();

        await refreshDashboard();

    }
);