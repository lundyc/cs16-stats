// app.js
// Fetches combined stats and renders dashboard, leaderboard, and admin actions chart

async function loadStats() {
  try {
    const response = await fetch("data/combined_stats.json");
    if (!response.ok) throw new Error("Failed to load stats JSON");
    const stats = await response.json();
    renderDashboard(stats);
    renderLeaderboard(stats);
    renderAdminChart(stats);
  } catch (err) {
    console.error("Error loading stats:", err);
  }
}

// ------------------------------
// Dashboard Cards
// ------------------------------
function renderDashboard(stats) {
  let totalMinutes = 0;
  let totalSlaps = 0;
  let totalBans = 0;
  let totalChats = 0;

  for (const name in stats) {
    const s = stats[name];
    totalMinutes += s.minutes || 0;
    totalSlaps += s.slap || 0;
    totalBans += s.ban || 0;
    totalChats += s.admin_chat || 0;
  }

  document.getElementById("total-minutes").textContent = totalMinutes.toLocaleString();
  document.getElementById("total-slaps").textContent = totalSlaps;
  document.getElementById("total-bans").textContent = totalBans;
  document.getElementById("total-chats").textContent = totalChats;
}

// ------------------------------
// Leaderboard Table
// ------------------------------
function renderLeaderboard(stats) {
  const tbody = document.getElementById("leaderboard-body");
  tbody.innerHTML = "";

  // Convert to array and sort
  const rows = Object.entries(stats).map(([name, s]) => ({ name, minutes: s.minutes || 0 }));
  rows.sort((a, b) => b.minutes - a.minutes);

  rows.forEach((row, i) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${i + 1}</td>
      <td>${row.name}</td>
      <td>${row.minutes.toLocaleString()}</td>
    `;
    tbody.appendChild(tr);
  });
}

// ------------------------------
// Admin Actions Chart
// ------------------------------
function renderAdminChart(stats) {
  const ctx = document.getElementById("adminChart").getContext("2d");

  const labels = Object.keys(stats);
  const slapData = labels.map(n => stats[n].slap || 0);
  const kickData = labels.map(n => stats[n].kick || 0);
  const banData = labels.map(n => stats[n].ban || 0);
  const renameData = labels.map(n => stats[n].rename || 0);
  const chatData = labels.map(n => stats[n].admin_chat || 0);

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        { label: "Slaps", data: slapData, backgroundColor: "rgba(220,53,69,0.7)" },
        { label: "Kicks", data: kickData, backgroundColor: "rgba(255,193,7,0.7)" },
        { label: "Bans", data: banData, backgroundColor: "rgba(13,110,253,0.7)" },
        { label: "Renames", data: renameData, backgroundColor: "rgba(111,66,193,0.7)" },
        { label: "Admin Chat", data: chatData, backgroundColor: "rgba(25,135,84,0.7)" },
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "top" },
        title: { display: true, text: "Admin Actions" }
      },
      scales: {
        x: { stacked: true },
        y: { stacked: true, beginAtZero: true }
      }
    }
  });
}

// ------------------------------
// Init
// ------------------------------
document.addEventListener("DOMContentLoaded", loadStats);
