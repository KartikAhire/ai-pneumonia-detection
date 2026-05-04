// Child Pneumonia Detection System - Main JavaScript

// Global variables
const currentTheme = localStorage.getItem("theme") || "light"

// Initialize application
document.addEventListener("DOMContentLoaded", () => {
  initializeTooltips()
  initializeModals()
  initializeFormValidation()
  initializeImagePreview()
  initializeNotifications()
})

// Bootstrap Tooltips
function initializeTooltips() {
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl))
}

// Bootstrap Modals
function initializeModals() {
  const modalElements = document.querySelectorAll(".modal")
  modalElements.forEach((modal) => {
    modal.addEventListener("show.bs.modal", function (event) {
      this.classList.add("fade-in")
    })
  })
}

// Form Validation
function initializeFormValidation() {
  const forms = document.querySelectorAll(".needs-validation")
  forms.forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!form.checkValidity()) {
        event.preventDefault()
        event.stopPropagation()
        showNotification("Please fill in all required fields correctly.", "error")
      }
      form.classList.add("was-validated")
    })
  })

  // Real-time validation
  const inputs = document.querySelectorAll("input, select, textarea")
  inputs.forEach((input) => {
    input.addEventListener("blur", function () {
      validateField(this)
    })
  })
}

function validateField(field) {
  const isValid = field.checkValidity()

  if (!isValid) {
    field.classList.add("is-invalid")
    field.classList.remove("is-valid")
  } else {
    field.classList.remove("is-invalid")
    field.classList.add("is-valid")
  }
}

// Image Preview Functionality
function initializeImagePreview() {
  const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]')
  imageInputs.forEach((input) => {
    input.addEventListener("change", (event) => {
      handleImagePreview(event)
    })
  })
}

function handleImagePreview(event) {
  const file = event.target.files[0]
  const previewContainer = document.getElementById("imagePreview")
  const previewImg = document.getElementById("previewImg")

  if (file && previewContainer && previewImg) {
    const reader = new FileReader()
    reader.onload = (e) => {
      previewImg.src = e.target.result
      previewContainer.style.display = "block"
      previewContainer.classList.add("fade-in")
    }
    reader.readAsDataURL(file)

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      showNotification("File size must be less than 10MB", "error")
      event.target.value = ""
      previewContainer.style.display = "none"
    }
  }
}

// Notification System
function initializeNotifications() {
  // Check for Django messages
  const messages = document.querySelectorAll(".django-message")
  messages.forEach((message) => {
    const type = message.dataset.type || "info"
    const text = message.textContent
    showNotification(text, type)
    message.remove()
  })
}

function showNotification(message, type = "info", duration = 5000) {
  const notification = document.createElement("div")
  notification.className = `alert alert-${getBootstrapAlertClass(type)} alert-dismissible fade show notification`
  notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    `

  notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `

  document.body.appendChild(notification)

  // Auto-remove after duration
  setTimeout(() => {
    if (notification.parentNode) {
      notification.remove()
    }
  }, duration)
}

function getBootstrapAlertClass(type) {
  const mapping = {
    success: "success",
    error: "danger",
    warning: "warning",
    info: "info",
  }
  return mapping[type] || "info"
}

function getNotificationIcon(type) {
  const mapping = {
    success: "check-circle",
    error: "exclamation-triangle",
    warning: "exclamation-circle",
    info: "info-circle",
  }
  return mapping[type] || "info-circle"
}

// Utility Functions
function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes"
  const k = 1024
  const sizes = ["Bytes", "KB", "MB", "GB"]
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

// Export functions for global use
window.PneumoniaDetection = {
  showNotification,
  formatFileSize,
  formatDate,
}
