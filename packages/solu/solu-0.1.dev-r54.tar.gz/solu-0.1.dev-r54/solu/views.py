#
# The Open Software License 3.0
#
# Copyright (c) 2008 Heikki Toivonen <My first name at heikkitoivonen.net>
#

from werkzeug import redirect
from werkzeug.exceptions import NotFound, BadRequest
from solu.utils import session, render_template, expose, \
     url_for, Pagination, session
from solu.models import Resource


@expose('/')
def index(request):
    """Home page, from which to search."""
    return render_template('index.html', title="Home")

@expose('/search_results/', defaults={'page': 1})
@expose('/search_results/<int:page>/')
def search_results(request, page):
    """Show search results."""
    name = request.values.get('name')    
    email = request.values.get('email')
    im = request.values.get('im')
    
    query = Resource.query
    if name:
        query = query.filter(Resource.name.like('%' + name + '%'))
    if email:
        query = query.filter(Resource.email.like('%' + email + '%'))
    if im:
        query = query.filter(Resource.im.like('%' + im + '%'))
    query = query.order_by(Resource.name)
    
    pagination = Pagination(query, 10, page, 'search_results',
                            name=name, email=email, im=im)
    if pagination.page > 1 and not pagination.entries:
        raise NotFound()
    
    return render_template('search_results.html', pagination=pagination,
                           title="Search Results")

@expose('/edit/<rid>')
def edit(request, rid):
    """Edit resource's information, including location."""
    resource = Resource.query.get(rid)
    if not resource:
        raise NotFound()
    if request.method == 'POST':
        name = request.form.get('name')
        x = request.form.get('x')
        y = request.form.get('y')
        check = request.form.get('check')
        if not name or not x or not y or check != resource.name:
            raise BadRequest()
        try:
            x = int(x, 10)
            y = int(y, 10)
        except ValueError:
            raise BadRequest()
        if not (0 < x < 800) or not (0 < y < 600):
            raise BadRequest()

        resource.name = name
        resource.email = request.form.get('email')
        resource.im = request.form.get('im')
        resource.x = x
        resource.y = y
        session.commit()
        return redirect(url_for('show', rid=resource.resource_id))
    return render_template('edit.html', resource=resource, title="Edit")

@expose('/add')
def add(request):
    """Add a new resource with location."""
    if request.method == 'POST':
        name = request.form.get('name')
        x = request.form.get('x')
        y = request.form.get('y')
        check = request.form.get('check')
        if not name or not x or not y or check != '3':
            raise BadRequest()
        try:
            x = int(x, 10)
            y = int(y, 10)
        except ValueError:
            raise BadRequest()
        if not (0 < x < 800) or not (0 < y < 600):
            raise BadRequest()

        resource = Resource(name,
                            request.form.get('email'),
                            request.form.get('im'),
                            x,
                            y
        )
        session.commit()
        return redirect(url_for('show', rid=resource.resource_id))
    return render_template('add.html', title="Add")

@expose('/show/<rid>')
def show(request, rid):
    """Show information and location of an existing resource."""
    resource = Resource.query.get(rid)
    if not resource:
        raise NotFound()
    return render_template('show.html', resource=resource, title="Show")

@expose('/delete/<rid>')
def delete(request, rid):
    """Delete a resource."""
    resource = Resource.query.get(rid)
    if not resource:
        raise NotFound()
    if request.method == 'POST':
        if request.form.get('check') != resource.name:
            raise BadRequest()
        session.delete(resource)
        session.commit()
        return redirect('/')
    return render_template('delete.html', resource=resource, title="Delete")
