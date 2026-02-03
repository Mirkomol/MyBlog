# Blog Routes

from flask import render_template, redirect, url_for, flash, request, current_app, abort, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid

from app.blog import blog_bp
from app.blog.forms import PostForm, SearchForm, AboutForm
from app.models import Post, Tag, User, SiteSettings
from app import db

# Gemini AI for blog generation
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_image(file):
    """Save uploaded image and return filename."""
    if file and allowed_file(file.filename):
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename
    return None


# ==================== PUBLIC ROUTES ====================

@blog_bp.route('/')
def index():
    """Homepage with featured and recent posts."""
    page = request.args.get('page', 1, type=int)
    
    # Get featured post
    featured_post = Post.query.filter_by(
        is_published=True, 
        is_featured=True
    ).order_by(Post.published_at.desc()).first()
    
    # Get recent posts (excluding featured)
    query = Post.query.filter_by(is_published=True)
    if featured_post:
        query = query.filter(Post.id != featured_post.id)
    
    posts = query.order_by(Post.published_at.desc()).paginate(
        page=page, 
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    
    # Get popular tags
    tags = Tag.query.join(Tag.posts).filter(Post.is_published == True).all()
    
    return render_template('index.html', 
                          featured_post=featured_post,
                          posts=posts,
                          tags=tags,
                          title='Home')


@blog_bp.route('/post/<slug>')
def view_post(slug):
    """View individual blog post."""
    post = Post.query.filter_by(slug=slug, is_published=True).first_or_404()
    
    # Increment view counter
    post.increment_views()
    
    # Get related posts (same tags)
    related_posts = []
    if post.tags:
        tag_ids = [tag.id for tag in post.tags]
        related_posts = Post.query.filter(
            Post.is_published == True,
            Post.id != post.id,
            Post.tags.any(Tag.id.in_(tag_ids))
        ).limit(3).all()
    
    return render_template('post.html', 
                          post=post,
                          related_posts=related_posts,
                          title=post.title)


@blog_bp.route('/tag/<slug>')
def posts_by_tag(slug):
    """View posts filtered by tag."""
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    
    posts = Post.query.filter(
        Post.is_published == True,
        Post.tags.contains(tag)
    ).order_by(Post.published_at.desc()).paginate(
        page=page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    
    return render_template('tag.html',
                          tag=tag,
                          posts=posts,
                          title=f'Posts tagged: {tag.name}')


@blog_bp.route('/search')
def search():
    """Search posts."""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if query:
        posts = Post.query.filter(
            Post.is_published == True,
            (Post.title.ilike(f'%{query}%') | Post.content.ilike(f'%{query}%'))
        ).order_by(Post.published_at.desc()).paginate(
            page=page,
            per_page=current_app.config['POSTS_PER_PAGE'],
            error_out=False
        )
    else:
        posts = None
    
    return render_template('search.html',
                          posts=posts,
                          query=query,
                          title=f'Search: {query}' if query else 'Search')


@blog_bp.route('/about')
def about():
    """About page."""
    # Get editable content from settings
    about_data = {
        'about_title': SiteSettings.get('about_title', 'Welcome to my blog'),
        'about_intro': SiteSettings.get('about_intro', 'Sharing thoughts, stories, and ideas with the world.'),
        'about_content': SiteSettings.get('about_content', ''),
        'twitter_url': SiteSettings.get('twitter_url', ''),
        'github_url': SiteSettings.get('github_url', ''),
        'linkedin_url': SiteSettings.get('linkedin_url', ''),
    }
    return render_template('about.html', title='About', about=about_data)


# ==================== ADMIN ROUTES ====================

@blog_bp.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard."""
    if not current_user.is_admin:
        abort(403)
    
    # Statistics
    total_posts = Post.query.count()
    published_posts = Post.query.filter_by(is_published=True).count()
    draft_posts = Post.query.filter_by(is_published=False).count()
    total_views = db.session.query(db.func.sum(Post.views)).scalar() or 0
    
    # Recent posts
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                          total_posts=total_posts,
                          published_posts=published_posts,
                          draft_posts=draft_posts,
                          total_views=total_views,
                          recent_posts=recent_posts,
                          title='Dashboard')


@blog_bp.route('/admin/posts')
@login_required
def admin_posts():
    """List all posts for admin."""
    if not current_user.is_admin:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    
    query = Post.query
    if status == 'published':
        query = query.filter_by(is_published=True)
    elif status == 'draft':
        query = query.filter_by(is_published=False)
    
    posts = query.order_by(Post.created_at.desc()).paginate(
        page=page,
        per_page=20,
        error_out=False
    )
    
    return render_template('admin/posts.html',
                          posts=posts,
                          status=status,
                          title='Manage Posts')


@blog_bp.route('/admin/posts/new', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create new blog post."""
    if not current_user.is_admin:
        abort(403)
    
    form = PostForm()
    
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            excerpt=form.excerpt.data,
            content=form.content.data,
            is_published=form.is_published.data,
            is_featured=form.is_featured.data,
            author_id=current_user.id
        )
        
        # Generate slug
        post.generate_slug()
        
        # Handle cover image
        if form.cover_image.data:
            filename = save_image(form.cover_image.data)
            if filename:
                post.cover_image = filename
        
        # Handle tags
        if form.tags.data:
            tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
            for tag_name in tag_names:
                tag = Tag.get_or_create(tag_name)
                post.tags.append(tag)
        
        # Set published date
        if form.is_published.data:
            post.published_at = datetime.utcnow()
        
        db.session.add(post)
        db.session.commit()
        
        flash('Post created successfully!', 'success')
        return redirect(url_for('blog.admin_posts'))
    
    return render_template('admin/post_form.html',
                          form=form,
                          title='New Post',
                          is_edit=False)


@blog_bp.route('/admin/posts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    """Edit existing blog post."""
    if not current_user.is_admin:
        abort(403)
    
    post = Post.query.get_or_404(id)
    form = PostForm(obj=post)
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.excerpt = form.excerpt.data
        post.content = form.content.data
        post.is_featured = form.is_featured.data
        
        # Handle publish status change
        was_published = post.is_published
        post.is_published = form.is_published.data
        if not was_published and form.is_published.data:
            post.published_at = datetime.utcnow()
        
        # Handle cover image
        if form.cover_image.data:
            filename = save_image(form.cover_image.data)
            if filename:
                # Delete old image if exists
                if post.cover_image:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], post.cover_image)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                post.cover_image = filename
        
        # Handle tags
        post.tags.clear()
        if form.tags.data:
            tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
            for tag_name in tag_names:
                tag = Tag.get_or_create(tag_name)
                post.tags.append(tag)
        
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('blog.admin_posts'))
    
    # Pre-populate tags
    if request.method == 'GET':
        form.tags.data = ', '.join([tag.name for tag in post.tags])
    
    return render_template('admin/post_form.html',
                          form=form,
                          post=post,
                          title='Edit Post',
                          is_edit=True)


@blog_bp.route('/admin/posts/<int:id>/delete', methods=['POST'])
@login_required
def delete_post(id):
    """Delete blog post."""
    if not current_user.is_admin:
        abort(403)
    
    post = Post.query.get_or_404(id)
    
    # Delete cover image if exists
    if post.cover_image:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], post.cover_image)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(post)
    db.session.commit()
    
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('blog.admin_posts'))


@blog_bp.route('/admin/posts/<int:id>/toggle-publish', methods=['POST'])
@login_required
def toggle_publish(id):
    """Toggle post publish status."""
    if not current_user.is_admin:
        abort(403)
    
    post = Post.query.get_or_404(id)
    post.is_published = not post.is_published
    
    if post.is_published and not post.published_at:
        post.published_at = datetime.utcnow()
    
    db.session.commit()
    
    status = 'published' if post.is_published else 'unpublished'
    flash(f'Post {status} successfully!', 'success')
    return redirect(url_for('blog.admin_posts'))


@blog_bp.route('/admin/about', methods=['GET', 'POST'])
@login_required
def admin_about():
    """Edit About page content."""
    if not current_user.is_admin:
        abort(403)
    
    form = AboutForm()
    
    if form.validate_on_submit():
        # Save all settings
        SiteSettings.set('about_title', form.about_title.data or '')
        SiteSettings.set('about_intro', form.about_intro.data or '')
        SiteSettings.set('about_content', form.about_content.data or '')
        SiteSettings.set('twitter_url', form.twitter_url.data or '')
        SiteSettings.set('github_url', form.github_url.data or '')
        SiteSettings.set('linkedin_url', form.linkedin_url.data or '')
        
        flash('About page updated successfully!', 'success')
        return redirect(url_for('blog.admin_about'))
    
    # Pre-populate form with existing values
    if request.method == 'GET':
        form.about_title.data = SiteSettings.get('about_title', '')
        form.about_intro.data = SiteSettings.get('about_intro', '')
        form.about_content.data = SiteSettings.get('about_content', '')
        form.twitter_url.data = SiteSettings.get('twitter_url', '')
        form.github_url.data = SiteSettings.get('github_url', '')
        form.linkedin_url.data = SiteSettings.get('linkedin_url', '')
    
    return render_template('admin/about_form.html',
                          form=form,
                          title='Edit About Page')


@blog_bp.route('/admin/generate-post', methods=['POST'])
@login_required
def generate_post():
    """Generate blog post content using Gemini AI."""
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if Gemini is available
    if not GEMINI_AVAILABLE:
        return jsonify({'error': 'Gemini AI library not installed'}), 500
    
    # Get API key
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        return jsonify({'error': 'GEMINI_API_KEY not configured. Add it to your environment variables.'}), 400
    
    # Get prompt from request
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'error': 'Please provide a topic or prompt'}), 400
    
    try:
        # Configure Gemini Client
        client = genai.Client(api_key=api_key)
        
        # Create blog post prompt
        blog_prompt = f"""Write a professional blog post about: {prompt}

Requirements:
- Write in a clear, engaging, and informative style
- Use proper headings (## for main sections, ### for subsections)
- Include an introduction and conclusion
- Be approximately 500-800 words
- Use markdown formatting
- Write in first person as a tech professional
- Make it SEO-friendly with relevant keywords

Return ONLY the blog content in markdown format, nothing else."""

        # Generate content
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=blog_prompt
        )
        content = response.text
        
        # Generate title
        title_prompt = f"Generate a catchy, SEO-friendly blog post title about: {prompt}. Return ONLY the title, nothing else."
        title_response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=title_prompt
        )
        title = title_response.text.strip().strip('"')
        
        # Generate excerpt
        excerpt_prompt = f"Write a 1-2 sentence summary/excerpt for a blog post about: {prompt}. Return ONLY the excerpt, nothing else."
        excerpt_response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=excerpt_prompt
        )
        excerpt = excerpt_response.text.strip()
        
        # Generate tags
        tags_prompt = f"Generate 3-5 relevant tags (single words or short phrases) for a blog post about: {prompt}. Return them comma-separated, nothing else."
        tags_response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=tags_prompt
        )
        tags = tags_response.text.strip()
        
        return jsonify({
            'success': True,
            'title': title,
            'content': content,
            'excerpt': excerpt,
            'tags': tags
        })
        
    except Exception as e:
        return jsonify({'error': f'AI generation failed: {str(e)}'}), 500
