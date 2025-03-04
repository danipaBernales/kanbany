# Kanbany

A modern task management application built with Django and Bootstrap, featuring a Kanban board interface.

## Features

- User authentication and authorization
- Kanban board interface
- Task creation and management
- Team collaboration
- Priority and status tracking
- Modern Minty theme from Bootswatch
- Responsive design

## Tech Stack

- Python 3.8+
- Django 4.2+
- PostgreSQL
- Bootstrap 5.3
- Font Awesome 6.0

## Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/kanbany.git
cd kanbany
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file:
```bash
cp .env.example .env
```
Edit the .env file with your local settings.

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

Visit http://localhost:8000 to access the application.

## Deployment

### GitHub Setup

1. Create a new repository on GitHub
2. Initialize git and push your code:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/kanbany.git
git push -u origin main
```

### Supabase Setup

1. Create a new project on Supabase
2. Get your database connection string
3. Update your .env file with the Supabase credentials:
```
DATABASE_URL=postgres://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```

### Netlify Deployment

1. Create a new site on Netlify
2. Connect your GitHub repository
3. Configure build settings:
   - Build command: `pip install -r requirements.txt`
   - Publish directory: `staticfiles`
4. Add environment variables from your .env file
5. Deploy!

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Bootstrap](https://getbootstrap.com/)
- [Bootswatch](https://bootswatch.com/)
- [Font Awesome](https://fontawesome.com/)
- [Django](https://www.djangoproject.com/)
