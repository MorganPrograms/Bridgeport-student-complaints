let selected = null;

document.getElementById("searchBox").addEventListener("input", async function() {
  const query = this.value;
  const res = await fetch("/search", {
    method: "POST",
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ query })
  });
  const data = await res.json();
  const container = document.getElementById("results");
  container.innerHTML = "";
  data.forEach(worker => {
    const div = document.createElement("div");
    div.textContent = `${worker.Name} (ID: ${worker.ID})`;
    div.onclick = () => {
      selected = worker;
      container.innerHTML = `Selected: ${worker.Name} - ${worker.ID}`;
    };
    container.appendChild(div);
  });
});

async function submitComplaint() {
  const message = document.getElementById("messageBox").value;
  if (!selected || !message.trim()) {
    alert("Please select a student and type your complaint.");
    return;
  }

  const res = await fetch("/submit", {
    method: "POST",
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      name: selected.Name,
      id: selected.ID,
      message
    })
  });

  const result = await res.json();
  document.getElementById("status").textContent = result.message;
}
