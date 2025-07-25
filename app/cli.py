"""Flask CLI commands for project management"""
import click
from flask.cli import with_appcontext
from app.extensions import db
from app.models import User, Category, Product, BlogPost, HomePageBlock, SocialLink
from app.utils import init_default_data

@click.command()
@with_appcontext
def init_db():
    """Initialize the database with tables and default data."""
    click.echo('Initializing database...')
    db.create_all()
    init_default_data()
    click.echo('Database initialized successfully!')

@click.command()
@with_appcontext
def reset_db():
    """Reset the database (WARNING: This will delete all data!)."""
    if click.confirm('This will delete all data. Are you sure?'):
        click.echo('Resetting database...')
        db.drop_all()
        db.create_all()
        init_default_data()
        click.echo('Database reset successfully!')

@click.command()
@click.option('--username', prompt='Username', help='Admin username')
@click.option('--email', prompt='Email', help='Admin email')
@click.option('--password', prompt='Password', hide_input=True, help='Admin password')
@with_appcontext
def create_admin(username, email, password):
    """Create a new admin user."""
    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        click.echo(f'User {username} already exists!')
        return
    
    # Create new admin user
    admin_user = User(
        username=username,
        email=email,
        is_admin=True
    )
    admin_user.set_password(password)
    
    db.session.add(admin_user)
    db.session.commit()
    
    click.echo(f'Admin user {username} created successfully!')

@click.command()
@with_appcontext
def list_users():
    """List all users in the system."""
    users = User.query.all()
    
    if not users:
        click.echo('No users found.')
        return
    
    click.echo('\nUsers:')
    click.echo('-' * 50)
    for user in users:
        status = 'Admin' if user.is_admin else 'User'
        click.echo(f'{user.id:>3} | {user.username:<20} | {user.email:<30} | {status}')

@click.command()
@with_appcontext
def stats():
    """Show database statistics."""
    stats_data = {
        'Users': User.query.count(),
        'Categories': Category.query.count(),
        'Products': Product.query.count(),
        'Blog Posts': BlogPost.query.count(),
        'Homepage Blocks': HomePageBlock.query.count(),
        'Social Links': SocialLink.query.count(),
    }
    
    click.echo('\nDatabase Statistics:')
    click.echo('-' * 30)
    for name, count in stats_data.items():
        click.echo(f'{name:<15}: {count:>5}')

def init_cli_commands(app):
    """Register CLI commands with the Flask app."""
    app.cli.add_command(init_db)
    app.cli.add_command(reset_db)
    app.cli.add_command(create_admin)
    app.cli.add_command(list_users)
    app.cli.add_command(stats)
