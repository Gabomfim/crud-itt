# Templates Directory 📄

This directory contains HTML templates that provide the web interface for the CRUD ITT application.

## 🎯 Purpose

The `templates/` directory houses Jinja2 HTML templates that render web pages for users, providing a visual interface beyond the API endpoints.

## 📁 Directory Structure

```
templates/
├── 404.html             # Custom 404 Not Found error page
└── index.html           # Main application homepage
```

## 📄 File Overview

### `index.html` - Homepage Template
**Purpose**: Main landing page for the web interface

**What it does**:
- Displays welcome message and application information
- Provides navigation to API documentation
- Shows basic application features and capabilities
- Serves as entry point for web-based interactions

**For beginners**: Think of this as the "front page" of your website - it's what users see when they first visit your application in a web browser.

### `404.html` - Error Page Template
**Purpose**: Custom error page for when users try to access non-existent pages

**What it does**:
- Shows user-friendly "Page Not Found" message
- Provides helpful navigation back to working parts of the app
- Maintains professional appearance during error scenarios
- Prevents users from seeing ugly default browser error pages

**For beginners**: This is like a "helpful sign" that appears when someone gets lost on your website - instead of showing a confusing error, it politely explains what happened and helps them find their way.

## 🌐 Template Integration

### FastAPI Template Setup
```python
# app.py
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Set up templates
templates = Jinja2Templates(directory="templates")

# Serve static files (CSS, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Homepage route
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "CRUD ITT - Home"}
    )

# Custom 404 handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(
        "404.html", 
        {"request": request, "title": "Page Not Found"},
        status_code=404
    )
```

### Template Context Variables
```python
# Passing data to templates
@app.get("/")
async def homepage(request: Request):
    context = {
        "request": request,
        "title": "CRUD ITT - User Management API",
        "version": "1.0.0",
        "features": [
            "User Registration",
            "Authentication", 
            "Password Management",
            "Profile Updates"
        ],
        "api_docs_url": "/docs"
    }
    return templates.TemplateResponse("index.html", context)
```

## 📋 Template Structure

### Basic HTML Template Structure
```html
<!-- Base structure for all templates -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    
    <!-- Styling -->
    <link rel="stylesheet" href="{{ url_for('static', path='/css/main.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', path='/css/error.css') }}">
    
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="container">
            <a href="/" class="navbar-brand">CRUD ITT</a>
            <div class="navbar-nav">
                <a href="/docs" class="nav-link">API Docs</a>
                <a href="/redoc" class="nav-link">ReDoc</a>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="main-content">
        <div class="container">
            {% block content %}
            <!-- Page-specific content goes here -->
            {% endblock %}
        </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 CRUD ITT. Built with FastAPI and love ❤️</p>
        </div>
    </footer>
</body>
</html>
```

### Template Inheritance Example
```html
<!-- base.html - Base template -->
<!DOCTYPE html>
<html lang="en">
<head>
    <title>{% block title %}CRUD ITT{% endblock %}</title>
    <!-- Common head elements -->
</head>
<body>
    {% include 'partials/navbar.html' %}
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    {% include 'partials/footer.html' %}
</body>
</html>

<!-- index.html - Extends base template -->
{% extends "base.html" %}

{% block title %}{{ super() }} - Homepage{% endblock %}

{% block content %}
<div class="hero-section">
    <h1>Welcome to CRUD ITT</h1>
    <p>A comprehensive user management API</p>
</div>
{% endblock %}
```

## 🎨 Styling Integration

### CSS Integration
```html
<!-- Link to static CSS files -->
<head>
    <link rel="stylesheet" href="{{ url_for('static', path='/css/main.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', path='/css/error.css') }}">
</head>
```

### Responsive Design
```html
<!-- Responsive meta tag -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- Responsive image example -->
<img src="{{ url_for('static', path='/images/logo.png') }}" 
     alt="CRUD ITT Logo" 
     class="responsive-image">
```

### Dark Mode Support
```html
<!-- Dark mode toggle -->
<head>
    <script>
        // Check for saved theme preference or default to light
        const theme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', theme);
    </script>
</head>

<!-- Theme toggle button -->
<button onclick="toggleTheme()" class="theme-toggle">
    🌙 Toggle Dark Mode
</button>

<script>
function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const target = current === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', target);
    localStorage.setItem('theme', target);
}
</script>
```

## 🔧 Dynamic Content

### Displaying API Data
```html
<!-- Show user count from API -->
<div class="stats-section">
    <div class="stat-card">
        <h3>{{ user_count }}</h3>
        <p>Registered Users</p>
    </div>
    <div class="stat-card">
        <h3>{{ api_version }}</h3>
        <p>API Version</p>
    </div>
</div>
```

### Conditional Content
```html
<!-- Show different content based on conditions -->
{% if user_authenticated %}
    <div class="welcome-message">
        <h2>Welcome back, {{ username }}!</h2>
        <a href="/profile" class="btn btn-primary">View Profile</a>
    </div>
{% else %}
    <div class="login-prompt">
        <h2>Get Started</h2>
        <p>Create an account or login to access all features</p>
        <a href="/docs" class="btn btn-primary">View API Documentation</a>
    </div>
{% endif %}
```

### Lists and Loops
```html
<!-- Display list of features -->
<div class="features-grid">
    {% for feature in features %}
    <div class="feature-card">
        <h3>{{ feature.title }}</h3>
        <p>{{ feature.description }}</p>
        <span class="feature-status">{{ feature.status }}</span>
    </div>
    {% endfor %}
</div>
```

## 📱 Interactive Elements

### Forms
```html
<!-- Contact form example -->
<form class="contact-form" method="post" action="/contact">
    <div class="form-group">
        <label for="name">Name:</label>
        <input type="text" id="name" name="name" required class="form-control">
    </div>
    
    <div class="form-group">
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" required class="form-control">
    </div>
    
    <div class="form-group">
        <label for="message">Message:</label>
        <textarea id="message" name="message" required class="form-control"></textarea>
    </div>
    
    <button type="submit" class="btn btn-primary">Send Message</button>
</form>
```

### JavaScript Integration
```html
<!-- Add interactivity with JavaScript -->
<script>
// Copy API endpoint to clipboard
function copyEndpoint(endpoint) {
    navigator.clipboard.writeText(endpoint).then(() => {
        showNotification('Endpoint copied to clipboard!');
    });
}

// Show notification
function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// API endpoint showcase
document.querySelectorAll('.endpoint-item').forEach(item => {
    item.addEventListener('click', () => {
        const endpoint = item.dataset.endpoint;
        copyEndpoint(endpoint);
    });
});
</script>
```

## 🛡️ Security Considerations

### XSS Prevention
```html
<!-- Jinja2 automatically escapes variables -->
<h1>Welcome {{ username }}!</h1>  <!-- Safe: automatically escaped -->

<!-- For raw HTML (use carefully) -->
<div>{{ content | safe }}</div>  <!-- Only if content is trusted -->

<!-- Manual escaping when needed -->
<div>{{ user_input | escape }}</div>
```

### CSRF Protection
```html
<!-- Include CSRF token in forms -->
<form method="post" action="/update-profile">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    <!-- Rest of form -->
</form>
```

### Content Security Policy
```html
<!-- Add CSP meta tag -->
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self';">
```

## 🎯 SEO and Accessibility

### SEO Meta Tags
```html
<head>
    <!-- Basic SEO -->
    <title>{{ title }} - CRUD ITT User Management API</title>
    <meta name="description" content="{{ description }}">
    <meta name="keywords" content="API, FastAPI, User Management, Authentication">
    
    <!-- Open Graph (social sharing) -->
    <meta property="og:title" content="{{ title }}">
    <meta property="og:description" content="{{ description }}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{{ request.url }}">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{{ title }}">
    <meta name="twitter:description" content="{{ description }}">
</head>
```

### Accessibility Features
```html
<!-- Semantic HTML -->
<main role="main">
    <section aria-labelledby="features-heading">
        <h2 id="features-heading">Key Features</h2>
        <!-- Content -->
    </section>
</main>

<!-- Skip navigation link -->
<a href="#main-content" class="skip-link">Skip to main content</a>

<!-- Alt text for images -->
<img src="/static/images/feature.png" 
     alt="User management dashboard screenshot">

<!-- Proper form labels -->
<label for="username">Username:</label>
<input type="text" id="username" name="username" aria-required="true">
```

## 🧪 Testing Templates

### Manual Testing
```bash
# Test different screen sizes
# Use browser developer tools to simulate:
# - Mobile: 375px width
# - Tablet: 768px width  
# - Desktop: 1200px width
```

### Accessibility Testing
```bash
# Use accessibility testing tools:
# - WAVE Web Accessibility Evaluator
# - axe DevTools browser extension
# - Lighthouse accessibility audit
```

### Performance Testing
```bash
# Test page load speed:
# - Google PageSpeed Insights
# - GTmetrix
# - WebPageTest
```

## 🎓 Learning Path

**Beginner**: 
1. Look at the existing HTML templates
2. Try changing text content and see the results
3. Learn basic HTML tags and structure
4. Understand how CSS styling is applied

**Intermediate**: 
1. Study Jinja2 template syntax and features
2. Learn about template inheritance and includes
3. Practice with forms and user interactions
4. Understand responsive design principles

**Advanced**: 
1. Implement complex template inheritance hierarchies
2. Create custom Jinja2 filters and functions
3. Optimize templates for performance
4. Integrate with frontend frameworks (React, Vue)

## 🔄 Development Workflow

### Adding New Templates
1. **Create HTML file** in `templates/` directory
2. **Set up route** in `app.py` to render the template
3. **Add CSS styling** in `static/css/` if needed
4. **Test responsiveness** on different screen sizes
5. **Validate HTML** and check for accessibility

### Template Organization
```
templates/
├── base.html              # Base template
├── index.html            # Homepage
├── 404.html              # Error page
├── auth/                 # Authentication templates
│   ├── login.html
│   └── register.html
├── user/                 # User management templates
│   ├── profile.html
│   └── settings.html
└── partials/             # Reusable template parts
    ├── navbar.html
    ├── footer.html
    └── breadcrumb.html
```

---

**Next**: Check out the [`scripts/`](../scripts/README.md) directory for utility scripts and automation tools!