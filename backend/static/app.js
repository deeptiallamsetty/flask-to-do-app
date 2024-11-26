const apiUrl = "http://127.0.0.1:5000"; // Change to your Flask app's URL
let token = null;

// User Registration
async function registerUser() {
  const username = document.getElementById("register-username").value;
  const password = document.getElementById("register-password").value;

  const response = await fetch(`${apiUrl}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  const data = await response.json();
  alert(data.message || "Registered successfully");
}

// User Login
async function loginUser() {
  const username = document.getElementById("login-username").value;
  const password = document.getElementById("login-password").value;

  const response = await fetch(`${apiUrl}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  if (response.ok) {
    const data = await response.json();
    token = data.access_token;
    document.getElementById("login").style.display = "none";
    document.getElementById("tasks").style.display = "block";
    fetchTasks();
  } else {
    alert("Login failed. Please check your credentials.");
  }
}

// Fetch Tasks
async function fetchTasks() {
  const response = await fetch(`${apiUrl}/tasks`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (response.ok) {
    const tasks = await response.json();
    const taskList = document.getElementById("task-list");
    taskList.innerHTML = "";
    tasks.forEach((task) => {
      const li = document.createElement("li");
      li.textContent = `${task.title}: ${task.description}`;
      const deleteButton = document.createElement("button");
      deleteButton.textContent = "Delete";
      deleteButton.onclick = () => deleteTask(task.id);
      li.appendChild(deleteButton);
      taskList.appendChild(li);
    });
  }
}

// Create Task
async function createTask() {
  const title = document.getElementById("task-title").value;
  const description = document.getElementById("task-desc").value;

  const response = await fetch(`${apiUrl}/tasks`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ title, description }),
  });

  if (response.ok) {
    fetchTasks();
  } else {
    alert("Failed to create task");
  }
}

// Delete Task
async function deleteTask(taskId) {
  const response = await fetch(`${apiUrl}/tasks/${taskId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });

  if (response.ok) {
    fetchTasks();
  } else {
    alert("Failed to delete task");
  }
}

// Logout
function logout() {
  token = null;
  document.getElementById("tasks").style.display = "none";
  document.getElementById("login").style.display = "block";
}
