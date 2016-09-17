from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from flask.ext.login import login_required

from app import db
from helpers import object_list
from models import Entry, Tag
from entries.forms import EntryForm

entries = Blueprint('entries', __name__, template_folder='templates')

def entry_list(template, query, **context):
    query = filter_status_by_user(query)

    valid_statuses = (Entry.STATUS_PUBLIC, Entry.STATUS_DRAFT)
    query = query.filter(Entry.status.in_(valid_statuses))
    if request.args.get('q'):
        search = request.args['q']
        query = query.filter(
                (Entry.body.contains(search)) |
                (Entry.title.contains(search)))
    return object_list(template, query, **context)

def get_entry_or_404(slug, author=None):
    # valid_statuses = (Entry.STATUS_PUBLIC, Entry.STATUS_DRAFT)
    # filter_ =  (Entry.slug == slug) & (Entry.status.in_(valid_statuses))
    # return Entry.query.filter(filter_).first_or_404()
    query = Entry.query.filter(Entry.slug == slug)
    if author:
        query = query.filter(Entry.author == author)
    else:
        query = filter_status_by_user(query)
    return query.first_or_404()

def filter_status_by_user(query):
    if not g.user.is_authenticated:
        query = query.filter(Entry.status == Entry.STATUS_PUBLIC)
    else:
        query = query.filter(
            (Entry.status == Entry.STATUS_PUBLIC) |
            ((Entry.author == g.user) &
             (Entry.status != Entry.STATUS_DELETED)))
    return query

@entries.route('/')
def index():
    entries = Entry.query.order_by(Entry.created_timestamp.desc())
    print entries.all()
    return entry_list('entries/index.html', entries)

@entries.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        form = EntryForm(request.form)
        if form.validate():
            entry = form.save_entry(Entry(author=g.user))
            db.session.add(entry)
            db.session.commit()
            flash('Entry "%s" created successfully.' % entry.title, 'success')
            return redirect(url_for('entries.detail', slug=entry.slug))
    else:
        form = EntryForm()
    return render_template('entries/create.html', form=form)

@entries.route('/tags/')
def tag_index():
    tags = Tag.query.order_by(Tag.name)
    return object_list('entries/tag_index.html', tags)

@entries.route('/tags/<slug>/')
def tag_detail(slug):
    tag = Tag.query.filter(Tag.slug == slug).first_or_404()
    entries = tag.entries.order_by(Entry.created_timestamp.desc())
    return entry_list('entries/tag_detail.html', entries, tag=tag)

@entries.route('/<slug>/')
def detail(slug):
    entry = get_entry_or_404(slug)
    return render_template('entries/detail.html', entry=entry)

@entries.route('/<slug>/edit/', methods=['GET', 'POST'])
@login_required
def edit(slug):
    entry = get_entry_or_404(slug, author=None)
    if request.method == 'POST':
        form = EntryForm(request.form, obj=entry)
        if form.validate():
            entry = form.save_entry(entry)
            db.session.add(entry)
            db.session.commit()
            flash('Entry "%s" has been saved.' % entry.title, 'success')
            return redirect(url_for('entries.detail', slug=entry.slug))
    else:
        form = EntryForm(obj=entry)
    return render_template('entries/edit.html', entry=entry, form=form)

@entries.route('/<slug>/delete/', methods=['GET', 'POST'])
@login_required
def delete(slug):
    entry = get_entry_or_404(slug, author=None)
    if request.method == 'POST':
        entry.status = Entry.STATUS_DELETED
        db.session.add(entry)
        db.session.commit()
        flash('Entry "%s" has been deleted.' % entry.title, 'success')
        return redirect(url_for('entries.index'))
    return render_template('entries/delete.html', entry=entry)

