import "./style.css";
import Chart from "chart.js/auto";


const API_BASE = "http://127.0.0.1:8000";

let regionChart = null;
let resultChart = null;
let latestResponse = null;


/* ---------------------------------------------------------
   Application Layout
--------------------------------------------------------- */

document.querySelector("#app").innerHTML = `
<div class="app-shell">

    <aside class="sidebar">

        <div class="brand">
            <div class="brand-icon">M</div>

            <div>
                <h1>MetricMind</h1>
                <p>Governed BI</p>
            </div>
        </div>

        <nav class="navigation">

            <button class="nav-item active" data-section="dashboard">
                <span>▦</span>
                Dashboard
            </button>

            <button class="nav-item" data-section="ask">
                <span>✦</span>
                Ask MetricMind
            </button>

            <button class="nav-item" data-section="metrics">
                <span>◆</span>
                Governed Metrics
            </button>

            <button class="nav-item" data-section="governance">
                <span>✓</span>
                Governance
            </button>

            <button class="nav-item" data-section="audit">
                <span>⌕</span>
                Audit Log
            </button>

        </nav>

        <div class="sidebar-footer">

            <div class="connection-card">

                <span
                    id="connectionDot"
                    class="status-dot"
                ></span>

                <div>
                    <strong id="connectionText">
                        Connecting...
                    </strong>

                    <small>
                        Semantic warehouse
                    </small>
                </div>

            </div>

        </div>

    </aside>


    <main class="main-content">

        <header class="topbar">

            <div>

                <p class="eyebrow">
                    GOVERNED ANALYTICS PLATFORM
                </p>

                <h2 id="pageTitle">
                    Executive Dashboard
                </h2>

            </div>

            <div class="topbar-right">

                <span class="governed-badge">
                    ✓ Governed Data
                </span>

                <span class="version-badge">
                    v1.0
                </span>

            </div>

        </header>


        <!-- =================================================
             DASHBOARD
        ================================================== -->

        <section
            id="dashboard"
            class="page-section active"
        >

            <div class="hero">

                <div>

                    <p class="eyebrow">
                        BUSINESS INTELLIGENCE
                    </p>

                    <h3>
                        Reliable metrics.
                        <br>
                        No metric hallucinations.
                    </h3>

                    <p>
                        MetricMind routes business questions
                        through a governed semantic layer before
                        querying analytical data.
                    </p>

                </div>

                <button
                    class="primary-button"
                    id="openAskButton"
                >
                    Ask your data →
                </button>

            </div>


            <div class="kpi-grid">

                <div class="kpi-card">
                    <span>Total Revenue</span>
                    <strong id="kpiRevenue">
                        Loading...
                    </strong>
                    <small>Governed revenue metric</small>
                </div>

                <div class="kpi-card">
                    <span>Total Profit</span>
                    <strong id="kpiProfit">
                        Loading...
                    </strong>
                    <small>After recorded costs</small>
                </div>

                <div class="kpi-card">
                    <span>Profit Margin</span>
                    <strong id="kpiMargin">
                        Loading...
                    </strong>
                    <small>Profit ÷ Revenue</small>
                </div>

                <div class="kpi-card">
                    <span>Total Orders</span>
                    <strong id="kpiOrders">
                        Loading...
                    </strong>
                    <small>Distinct transactions</small>
                </div>

            </div>


            <div class="dashboard-grid">

                <div class="panel chart-panel">

                    <div class="panel-header">

                        <div>
                            <p class="eyebrow">
                                REGIONAL PERFORMANCE
                            </p>

                            <h3>
                                Revenue by Region
                            </h3>
                        </div>

                        <span class="verified-tag">
                            ✓ Semantic verified
                        </span>

                    </div>

                    <div class="chart-container">
                        <canvas id="regionChart"></canvas>
                    </div>

                </div>


                <div class="panel insight-panel">

                    <p class="eyebrow">
                        GOVERNED INSIGHT
                    </p>

                    <h3>
                        Highest Revenue Region
                    </h3>

                    <div
                        id="dashboardInsight"
                        class="large-insight"
                    >
                        Loading analytics...
                    </div>

                    <div class="governance-note">
                        This result is calculated using
                        the centrally defined
                        <strong>Total Revenue</strong>
                        semantic metric.
                    </div>

                </div>

            </div>

        </section>


        <!-- =================================================
             ASK METRICMIND
        ================================================== -->

        <section
            id="ask"
            class="page-section"
        >

            <div class="section-heading">

                <p class="eyebrow">
                    CONVERSATIONAL BI
                </p>

                <h3>
                    Ask MetricMind
                </h3>

                <p>
                    Ask business questions using natural
                    language. MetricMind resolves them through
                    governed metrics instead of unrestricted SQL.
                </p>

            </div>


            <div class="ask-layout">

                <div class="panel ask-panel">

                    <label for="questionInput">
                        Business question
                    </label>

                    <textarea
                        id="questionInput"
                        placeholder="Example: Why did European profit margin drop in Q3 2026?"
                    ></textarea>

                    <div class="suggestion-row">

                        <button
                            class="suggestion"
                            data-question="What is our total revenue?"
                        >
                            Total revenue
                        </button>

                        <button
                            class="suggestion"
                            data-question="Show revenue by region"
                        >
                            Revenue by region
                        </button>

                        <button
                            class="suggestion"
                            data-question="What was European profit margin in Q3 2026?"
                        >
                            Europe Q3 margin
                        </button>

                        <button
                            class="suggestion"
                            data-question="Why did European profit margin drop in Q3 2026?"
                        >
                            Explain Q3 margin
                        </button>

                    </div>

                    <button
                        id="askButton"
                        class="primary-button full-button"
                    >
                        Ask MetricMind
                    </button>

                </div>


                <div class="panel response-panel">

                    <div class="panel-header">

                        <div>
                            <p class="eyebrow">
                                ANALYTICAL RESPONSE
                            </p>

                            <h3>
                                MetricMind Answer
                            </h3>
                        </div>

                        <span
                            id="answerMode"
                            class="mode-badge"
                        >
                            Waiting
                        </span>

                    </div>

                    <div
                        id="answerContent"
                        class="answer-content empty-state"
                    >
                        Ask a business question to begin.
                    </div>

                    <div
                        id="resultChartContainer"
                        class="result-chart-container hidden"
                    >
                        <canvas id="resultChart"></canvas>
                    </div>

                </div>

            </div>


            <div
                id="queryTransparency"
                class="panel transparency-panel hidden"
            >

                <div class="panel-header">

                    <div>
                        <p class="eyebrow">
                            TRANSPARENCY
                        </p>

                        <h3>
                            Governance & Query Details
                        </h3>
                    </div>

                    <span class="verified-tag">
                        ✓ Governed
                    </span>

                </div>


                <div class="transparency-grid">

                    <div>
                        <span class="detail-label">
                            Metric
                        </span>

                        <strong id="detailMetric">
                            —
                        </strong>
                    </div>

                    <div>
                        <span class="detail-label">
                            Definition
                        </span>

                        <code id="detailDefinition">
                            —
                        </code>
                    </div>

                    <div>
                        <span class="detail-label">
                            Filters
                        </span>

                        <code id="detailFilters">
                            —
                        </code>
                    </div>

                </div>


                <details class="query-details">

                    <summary>
                        View generated query
                    </summary>

                    <pre id="detailQuery"></pre>

                </details>

            </div>

        </section>


        <!-- =================================================
             METRICS
        ================================================== -->

        <section
            id="metrics"
            class="page-section"
        >

            <div class="section-heading">

                <p class="eyebrow">
                    SEMANTIC LAYER
                </p>

                <h3>
                    Governed Metrics
                </h3>

                <p>
                    Every business measure has one centralized,
                    auditable definition.
                </p>

            </div>

            <div
                id="metricGrid"
                class="metric-grid"
            >
                Loading metrics...
            </div>

        </section>


        <!-- =================================================
             GOVERNANCE
        ================================================== -->

        <section
            id="governance"
            class="page-section"
        >

            <div class="section-heading">

                <p class="eyebrow">
                    TRUST & TRANSPARENCY
                </p>

                <h3>
                    Semantic Governance
                </h3>

                <p>
                    MetricMind prevents unrestricted business
                    metric generation by enforcing centrally
                    governed definitions.
                </p>

            </div>


            <div class="governance-flow">

                <div class="flow-card">
                    <span>01</span>
                    <strong>Business Question</strong>
                    <p>
                        User asks a natural-language question.
                    </p>
                </div>

                <div class="flow-arrow">→</div>

                <div class="flow-card">
                    <span>02</span>
                    <strong>Intent Detection</strong>
                    <p>
                        Metric, filters and grouping are detected.
                    </p>
                </div>

                <div class="flow-arrow">→</div>

                <div class="flow-card highlight">
                    <span>03</span>
                    <strong>Semantic Layer</strong>
                    <p>
                        Approved metric definition is retrieved.
                    </p>
                </div>

                <div class="flow-arrow">→</div>

                <div class="flow-card">
                    <span>04</span>
                    <strong>Governed Query</strong>
                    <p>
                        Parameterized query accesses the warehouse.
                    </p>
                </div>

                <div class="flow-arrow">→</div>

                <div class="flow-card">
                    <span>05</span>
                    <strong>Audited Result</strong>
                    <p>
                        Result and query metadata are recorded.
                    </p>
                </div>

            </div>


            <div class="panel governance-example">

                <p class="eyebrow">
                    EXAMPLE METRIC
                </p>

                <h3>
                    Profit Margin
                </h3>

                <pre>
(SUM(profit) / NULLIF(SUM(revenue), 0)) * 100
                </pre>

                <p>
                    Every request for profit margin uses this
                    definition. The conversational layer cannot
                    silently substitute a different formula.
                </p>

            </div>

        </section>


        <!-- =================================================
             AUDIT
        ================================================== -->

        <section
            id="audit"
            class="page-section"
        >

            <div class="section-heading">

                <p class="eyebrow">
                    QUERY TRACEABILITY
                </p>

                <h3>
                    Audit Log
                </h3>

                <p>
                    Review questions, detected metrics,
                    filters and governance status.
                </p>

            </div>


            <div class="panel">

                <div class="table-wrapper">

                    <table>

                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Question</th>
                                <th>Mode</th>
                                <th>Metric</th>
                                <th>Filters</th>
                                <th>Status</th>
                                <th>Time</th>
                            </tr>
                        </thead>

                        <tbody id="auditBody">

                            <tr>
                                <td colspan="7">
                                    Loading audit history...
                                </td>
                            </tr>

                        </tbody>

                    </table>

                </div>

            </div>

        </section>

    </main>

</div>
`;


/* ---------------------------------------------------------
   Utilities
--------------------------------------------------------- */

async function requestAPI(
    endpoint,
    options = {}
) {

    const response = await fetch(
        `${API_BASE}${endpoint}`,
        options
    );

    if (!response.ok) {

        let message = "Request failed.";

        try {

            const error = await response.json();

            message =
                error.detail ||
                message;

        } catch {
            // Keep default message
        }

        throw new Error(message);
    }

    return response.json();
}


function escapeHTML(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


async function askAPI(question) {

    return requestAPI(
        "/api/ask",
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({
                question
            })
        }
    );
}


/* ---------------------------------------------------------
   Health
--------------------------------------------------------- */

async function checkHealth() {

    const dot =
        document.querySelector(
            "#connectionDot"
        );

    const text =
        document.querySelector(
            "#connectionText"
        );

    try {

        await requestAPI("/health");

        dot.classList.add("online");

        text.textContent =
            "Data Connected";

    } catch {

        dot.classList.remove("online");

        text.textContent =
            "API Offline";
    }
}


/* ---------------------------------------------------------
   Navigation
--------------------------------------------------------- */

const pageTitles = {

    dashboard:
        "Executive Dashboard",

    ask:
        "Ask MetricMind",

    metrics:
        "Governed Metrics",

    governance:
        "Semantic Governance",

    audit:
        "Query Audit Log"
};


function openSection(sectionName) {

    document
        .querySelectorAll(
            ".page-section"
        )
        .forEach(section => {

            section.classList.remove(
                "active"
            );
        });


    document
        .querySelector(
            `#${sectionName}`
        )
        .classList.add(
            "active"
        );


    document
        .querySelectorAll(
            ".nav-item"
        )
        .forEach(item => {

            item.classList.remove(
                "active"
            );
        });


    document
        .querySelector(
            `[data-section="${sectionName}"]`
        )
        ?.classList.add(
            "active"
        );


    document.querySelector(
        "#pageTitle"
    ).textContent =
        pageTitles[sectionName];


    if (sectionName === "metrics") {
        loadMetrics();
    }

    if (sectionName === "audit") {
        loadAudit();
    }
}


document
    .querySelectorAll(
        ".nav-item"
    )
    .forEach(button => {

        button.addEventListener(
            "click",
            () => {

                openSection(
                    button.dataset.section
                );
            }
        );
    });


document
    .querySelector(
        "#openAskButton"
    )
    .addEventListener(
        "click",
        () => openSection("ask")
    );


/* ---------------------------------------------------------
   Dashboard
--------------------------------------------------------- */

async function loadDashboard() {

    try {

        const [
            revenue,
            profit,
            margin,
            orders,
            regional
        ] = await Promise.all([

            askAPI(
                "What is our total revenue?"
            ),

            askAPI(
                "What is our total profit?"
            ),

            askAPI(
                "What is our profit margin?"
            ),

            askAPI(
                "How many orders do we have?"
            ),

            askAPI(
                "Show revenue by region"
            )
        ]);


        document.querySelector(
            "#kpiRevenue"
        ).textContent =
            revenue.results[0]
                .formatted_value;


        document.querySelector(
            "#kpiProfit"
        ).textContent =
            profit.results[0]
                .formatted_value;


        document.querySelector(
            "#kpiMargin"
        ).textContent =
            margin.results[0]
                .formatted_value;


        document.querySelector(
            "#kpiOrders"
        ).textContent =
            orders.results[0]
                .formatted_value;


        document.querySelector(
            "#dashboardInsight"
        ).textContent =
            regional.answer;


        renderRegionChart(
            regional.results
        );

    } catch (error) {

        document.querySelector(
            "#dashboardInsight"
        ).textContent =
            `Dashboard error: ${error.message}`;
    }
}


function renderRegionChart(results) {

    const labels =
        results.map(
            item => item.dimension
        );

    const values =
        results.map(
            item => item.value
        );


    if (regionChart) {
        regionChart.destroy();
    }


    const canvas =
        document.querySelector(
            "#regionChart"
        );


    regionChart =
        new Chart(
            canvas,
            {
                type: "bar",

                data: {
                    labels,

                    datasets: [
                        {
                            label:
                                "Revenue",

                            data:
                                values,

                            borderRadius:
                                7,

                            borderWidth:
                                0
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
                        },

                        tooltip: {

                            callbacks: {

                                label:
                                    context => {

                                        return (
                                            "$" +
                                            Number(
                                                context.raw
                                            )
                                            .toLocaleString()
                                        );
                                    }
                            }
                        }
                    },

                    scales: {

                        y: {
                            beginAtZero: true,

                            ticks: {

                                callback:
                                    value => {

                                        return (
                                            "$" +
                                            (
                                                value /
                                                1000000
                                            )
                                            .toFixed(1)
                                            +
                                            "M"
                                        );
                                    }
                            }
                        },

                        x: {
                            grid: {
                                display:
                                    false
                            }
                        }
                    }
                }
            }
        );
}


/* ---------------------------------------------------------
   Ask MetricMind
--------------------------------------------------------- */

document
    .querySelector(
        "#askButton"
    )
    .addEventListener(
        "click",
        submitCurrentQuestion
    );


document
    .querySelectorAll(
        ".suggestion"
    )
    .forEach(button => {

        button.addEventListener(
            "click",
            () => {

                document.querySelector(
                    "#questionInput"
                ).value =
                    button.dataset.question;

                submitCurrentQuestion();
            }
        );
    });


document
    .querySelector(
        "#questionInput"
    )
    .addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter" &&
                (event.ctrlKey ||
                 event.metaKey)
            ) {

                submitCurrentQuestion();
            }
        }
    );


async function submitCurrentQuestion() {

    const input =
        document.querySelector(
            "#questionInput"
        );

    const question =
        input.value.trim();


    if (!question) {

        input.focus();

        return;
    }


    const answer =
        document.querySelector(
            "#answerContent"
        );


    answer.classList.remove(
        "empty-state"
    );


    answer.innerHTML = `
        <div class="loading-state">
            Analyzing governed metrics...
        </div>
    `;


    document.querySelector(
        "#answerMode"
    ).textContent =
        "Processing";


    try {

        const response =
            await askAPI(question);

        latestResponse =
            response;

        renderAnswer(
            response
        );

        renderTransparency(
            response
        );

    } catch (error) {

        answer.innerHTML = `
            <div class="error-message">
                ${escapeHTML(
                    error.message
                )}
            </div>
        `;

        document.querySelector(
            "#answerMode"
        ).textContent =
            "Error";
    }
}


function renderAnswer(response) {

    const container =
        document.querySelector(
            "#answerContent"
        );


    const chartContainer =
        document.querySelector(
            "#resultChartContainer"
        );


    chartContainer.classList.add(
        "hidden"
    );


    if (resultChart) {

        resultChart.destroy();

        resultChart = null;
    }


    if (
        response.mode ===
        "root_cause_analysis"
    ) {

        document.querySelector(
            "#answerMode"
        ).textContent =
            "Root Cause";


        container.innerHTML = `

            <div class="answer-main">

                <span class="answer-icon">
                    ✦
                </span>

                <p>
                    ${escapeHTML(
                        response.explanation
                    )}
                </p>

            </div>


            <div class="analysis-stats">

                <div>
                    <span>
                        Previous Margin
                    </span>

                    <strong>
                        ${
                            response
                            .previous_margin
                            .toFixed(2)
                        }%
                    </strong>
                </div>

                <div>
                    <span>
                        Current Margin
                    </span>

                    <strong>
                        ${
                            response
                            .current_margin
                            .toFixed(2)
                        }%
                    </strong>
                </div>

                <div>
                    <span>
                        Change
                    </span>

                    <strong>
                        ${
                            response
                            .margin_change_percentage_points
                            .toFixed(2)
                        } pp
                    </strong>
                </div>

                <div>
                    <span>
                        Primary Driver
                    </span>

                    <strong>
                        ${escapeHTML(
                            response.primary_driver
                        )}
                    </strong>
                </div>

            </div>
        `;


        chartContainer.classList.remove(
            "hidden"
        );


        renderCostDriverChart(
            response.cost_drivers
        );

        return;
    }


    document.querySelector(
        "#answerMode"
    ).textContent =
        "Governed Query";


    container.innerHTML = `

        <div class="answer-main">

            <span class="answer-icon">
                ✓
            </span>

            <p>
                ${escapeHTML(
                    response.answer
                )}
            </p>

        </div>
    `;


    if (
        response.group_by &&
        response.results.length > 1
    ) {

        chartContainer.classList.remove(
            "hidden"
        );

        renderGroupedChart(
            response
        );
    }
}


function renderGroupedChart(
    response
) {

    const labels =
        response.results.map(
            item => item.dimension
        );

    const values =
        response.results.map(
            item => item.value
        );


    resultChart =
        new Chart(
            document.querySelector(
                "#resultChart"
            ),
            {
                type: "bar",

                data: {

                    labels,

                    datasets: [
                        {
                            label:
                                response.metric_label,

                            data:
                                values,

                            borderRadius:
                                7
                        }
                    ]
                },

                options: {

                    responsive:
                        true,

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
                                true
                        },

                        x: {
                            grid: {
                                display:
                                    false
                            }
                        }
                    }
                }
            }
        );
}


function renderCostDriverChart(
    drivers
) {

    resultChart =
        new Chart(
            document.querySelector(
                "#resultChart"
            ),
            {
                type: "bar",

                data: {

                    labels:
                        drivers.map(
                            item =>
                                item.name
                        ),

                    datasets: [
                        {
                            label:
                                "Change in cost share (pp)",

                            data:
                                drivers.map(
                                    item =>
                                        item.change_percentage_points
                                ),

                            borderRadius:
                                7
                        }
                    ]
                },

                options: {

                    responsive:
                        true,

                    maintainAspectRatio:
                        false,

                    plugins: {

                        legend: {
                            display: false
                        }
                    },

                    scales: {

                        x: {
                            grid: {
                                display:
                                    false
                            }
                        }
                    }
                }
            }
        );
}


/* ---------------------------------------------------------
   Transparency
--------------------------------------------------------- */

function renderTransparency(
    response
) {

    const panel =
        document.querySelector(
            "#queryTransparency"
        );


    panel.classList.remove(
        "hidden"
    );


    if (
        response.mode ===
        "root_cause_analysis"
    ) {

        document.querySelector(
            "#detailMetric"
        ).textContent =
            "Profit Margin";


        document.querySelector(
            "#detailDefinition"
        ).textContent =
            "Governed period comparison";


        document.querySelector(
            "#detailFilters"
        ).textContent =
            JSON.stringify({
                region:
                    response.region,

                year:
                    response
                    .current_period
                    .year,

                quarter:
                    response
                    .current_period
                    .quarter
            });


        document.querySelector(
            "#detailQuery"
        ).textContent =
            "Governed Q2/Q3 period comparison and cost-driver analysis.";

        return;
    }


    document.querySelector(
        "#detailMetric"
    ).textContent =
        response.metric_label;


    document.querySelector(
        "#detailDefinition"
    ).textContent =
        response.metric_definition;


    document.querySelector(
        "#detailFilters"
    ).textContent =
        JSON.stringify(
            response.filters
        );


    document.querySelector(
        "#detailQuery"
    ).textContent =
        response.query;
}


/* ---------------------------------------------------------
   Metrics
--------------------------------------------------------- */

let metricsLoaded = false;


async function loadMetrics() {

    if (metricsLoaded) {
        return;
    }


    const grid =
        document.querySelector(
            "#metricGrid"
        );


    try {

        const response =
            await requestAPI(
                "/api/metrics"
            );


        grid.innerHTML =
            response.metrics
            .map(
                metric => `

                <div class="metric-card">

                    <div class="metric-card-top">

                        <span class="metric-icon">
                            ◆
                        </span>

                        <span class="verified-tag">
                            ✓ Governed
                        </span>

                    </div>

                    <h4>
                        ${escapeHTML(
                            metric.label
                        )}
                    </h4>

                    <code>
                        ${escapeHTML(
                            metric.definition
                        )}
                    </code>

                    <p>
                        ${escapeHTML(
                            metric.description
                        )}
                    </p>

                </div>
                `
            )
            .join("");


        metricsLoaded = true;

    } catch (error) {

        grid.innerHTML = `
            <div class="error-message">
                ${escapeHTML(
                    error.message
                )}
            </div>
        `;
    }
}


/* ---------------------------------------------------------
   Audit
--------------------------------------------------------- */

async function loadAudit() {

    const body =
        document.querySelector(
            "#auditBody"
        );


    body.innerHTML = `
        <tr>
            <td colspan="7">
                Loading audit history...
            </td>
        </tr>
    `;


    try {

        const response =
            await requestAPI(
                "/api/audit?limit=50"
            );


        if (
            response.history.length === 0
        ) {

            body.innerHTML = `
                <tr>
                    <td colspan="7">
                        No queries recorded yet.
                    </td>
                </tr>
            `;

            return;
        }


        body.innerHTML =
            response.history
            .map(
                item => `

                <tr>

                    <td>
                        #${item.id}
                    </td>

                    <td class="question-cell">
                        ${escapeHTML(
                            item.question
                        )}
                    </td>

                    <td>
                        ${escapeHTML(
                            item.mode
                        )}
                    </td>

                    <td>
                        ${escapeHTML(
                            item.metric || "—"
                        )}
                    </td>

                    <td>
                        <code>
                            ${escapeHTML(
                                JSON.stringify(
                                    item.filters
                                )
                            )}
                        </code>
                    </td>

                    <td>
                        ${
                            item.governed
                            ?
                            `<span class="verified-tag">
                                ✓ Governed
                            </span>`
                            :
                            "Unverified"
                        }
                    </td>

                    <td>
                        ${
                            new Date(
                                item.created_at
                            )
                            .toLocaleString()
                        }
                    </td>

                </tr>
                `
            )
            .join("");

    } catch (error) {

        body.innerHTML = `
            <tr>
                <td colspan="7">
                    ${escapeHTML(
                        error.message
                    )}
                </td>
            </tr>
        `;
    }
}


/* ---------------------------------------------------------
   Initialize
--------------------------------------------------------- */

checkHealth();
loadDashboard();