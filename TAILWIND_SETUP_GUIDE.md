# Tailwind CSS Setup Guide for Django

## Method 1: CDN (Quick Setup - Recommended for now)
Add this to your base template head section:

```html
<script src="https://cdn.tailwindcss.com"></script>
<script>
  tailwind.config = {
    theme: {
      extend: {
        colors: {
          primary: {
            50: '#eff6ff',
            500: '#3b82f6',
            600: '#2563eb',
            700: '#1d4ed8',
            900: '#1e3a8a',
          }
        }
      }
    }
  }
</script>
```

## Method 2: Full Installation (Production Ready)

1. **Install Node.js** (if not installed):
   - Download from https://nodejs.org/
   - Install the LTS version

2. **Initialize npm in your project root**:
   ```bash
   npm init -y
   ```

3. **Install Tailwind CSS**:
   ```bash
   npm install -D tailwindcss
   npx tailwindcss init
   ```

4. **Configure tailwind.config.js**:
   ```javascript
   module.exports = {
     content: ["./templates/**/*.html", "./static/**/*.js"],
     theme: {
       extend: {
         colors: {
           primary: {
             50: '#eff6ff',
             500: '#3b82f6',
             600: '#2563eb',
             700: '#1d4ed8',
             900: '#1e3a8a',
           }
         }
       },
     },
     plugins: [],
   }
   ```

5. **Create input CSS file** (static/css/tailwind-input.css):
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

6. **Build CSS**:
   ```bash
   npx tailwindcss -i ./static/css/tailwind-input.css -o ./static/css/tailwind-output.css --watch
   ```

7. **Include in your templates**:
   ```html
   <link href="{% static 'css/tailwind-output.css' %}" rel="stylesheet">
   ```

## For now, let's use Method 1 (CDN) to get started quickly!