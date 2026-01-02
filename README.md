# Barta Django Project

## Project Structure Created:

### 1. Django Project: **Barta**
- Main project configuration in `Barta/` directory
- Configured settings with proper app registration

### 2. Django App: **core**
- Core application created with standard Django structure
- URLs configured and linked to main project

### 3. Directory Configuration:

#### Static Files:
- `STATIC_URL = '/static/'`
- `STATIC_ROOT = BASE_DIR / 'staticfiles'` (for production collected static files)
- `STATICFILES_DIRS = [BASE_DIR / 'static']` (for development static files)
- Created subdirectories:
  - `static/css/` - CSS stylesheets
  - `static/js/` - JavaScript files
  - `static/images/` - Image assets

#### Media Files:
- `MEDIA_URL = '/media/'`
- `MEDIA_ROOT = BASE_DIR / 'media'` (for user uploaded files)

### 4. URL Configuration:
- Main URLs in `Barta/urls.py`:
  - Admin panel: `/admin/`
  - Core app URLs included at root: `/`
  - Media and static files serving configured for DEBUG mode

- Core app URLs in `core/urls.py`:
  - Ready to add custom URL patterns

## Next Steps:

1. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

3. Run the development server:
   ```bash
   python manage.py runserver
   ```

4. Start building your views, models, and templates in the core app!

## Files Modified/Created:
- ✅ `Barta/settings.py` - Added core app, configured static and media settings
- ✅ `Barta/urls.py` - Configured URL routing with core app and media serving
- ✅ `core/urls.py` - Created URL configuration for core app
- ✅ `static/` directory structure
- ✅ `media/` directory
- ✅ `staticfiles/` directory
