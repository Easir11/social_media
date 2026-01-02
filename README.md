# Barta 4.0 - Social Media Platform

A modern, feature-rich social media platform built with Django, designed for connecting people through posts, follows, messaging, and more.

## 🚀 Features

### Core Functionality
- **User Authentication**: Secure login/signup with Google OAuth integration
- **User Profiles**: Customizable profiles with pictures, bio, location, and statistics
- **Posts & Interactions**: Create, edit, delete posts with emoji reactions and comments
- **Follow System**: Follow/unfollow users, view followers and following lists
- **News Feed**: Personalized feed showing posts from followed users
- **Messaging**: Private messaging system with conversation threads
- **Notifications**: Real-time notifications for interactions and activities

### Advanced Features
- **Smart Search**: Intelligent user search with fuzzy matching
- **Friend Suggestions**: AI-powered recommendations based on mutual connections
- **Media Uploads**: Support for profile pictures, cover photos, and post images
- **Responsive Design**: Mobile-friendly interface with Bootstrap styling
- **Real-time Updates**: Dynamic content loading and updates

## 🛠️ Tech Stack

- **Backend**: Django 3.2
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: Django Allauth with Google OAuth
- **Icons**: Font Awesome
- **Environment**: Python 3.8+

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Easir11/social_media.git
   cd social_media
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   - Copy `.env.example` to `.env` (if available) or create `.env` file
   - Add your Google OAuth credentials:
     ```
     GOOGLE_CLIENT_ID=your_google_client_id
     GOOGLE_CLIENT_SECRET=your_google_client_secret
     ```

5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Load sample data (optional)**
   ```bash
   python manage.py create_sample_data
   ```

## 🚀 Running the Application

1. **Activate virtual environment**
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Start development server**
   ```bash
   python manage.py runserver
   ```

3. **Access the application**
   - Open http://127.0.0.1:8000 in your browser
   - Login with your account or create a new one

## 📁 Project Structure

```
Barta/
├── Barta/                 # Django project settings
│   ├── settings.py       # Main settings file
│   ├── urls.py          # URL configurations
│   └── wsgi.py          # WSGI application
├── core/                 # Main application
│   ├── models.py        # Database models
│   ├── views.py         # View functions
│   ├── urls.py          # App URLs
│   ├── templates/       # HTML templates
│   └── static/          # CSS, JS, images
├── media/               # User uploaded files
├── static/              # Static files
├── templates/           # Base templates
└── manage.py            # Django management script
```

## 🔐 Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
SECRET_KEY=your_django_secret_key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

## 🧪 Testing

Run the test suite:

```bash
python manage.py test
```

## 📱 API Endpoints

### Authentication
- `/accounts/login/` - User login
- `/accounts/signup/` - User registration
- `/accounts/google/login/` - Google OAuth login

### Core Features
- `/` - Home feed
- `/profile/<username>/` - User profiles
- `/find-friends/` - User search
- `/messages/` - Messaging system
- `/notifications/` - User notifications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Easir Arafat** - *Initial work* - [Easir11](https://github.com/Easir11)

## 🙏 Acknowledgments

- Django community for the excellent framework
- Bootstrap for the responsive UI components
- Font Awesome for the beautiful icons
- Google OAuth for seamless authentication

## 📞 Support

If you have any questions or issues, please open an issue on GitHub or contact the maintainers.

---

**Note**: This is a development version. For production deployment, ensure proper security configurations and use a production-grade database like PostgreSQL.