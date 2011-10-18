# -*- coding: utf-8 -*-
"""
    Pool Server
    ~~~~~~
    a server to handle resources pool of STBs for testing

    :copyright: (c) 2011 by Israel Fruchter.
    :license: BSD, see LICENSE for more details.
"""

#TODO: arping for mac retrieval
# http://www.ibm.com/developerworks/aix/library/au-pythocli/

import re
from flask import Flask, request, redirect, url_for, \
     render_template, jsonify, flash
from ResourcePool import Resource, ObjectPool, IntegrityError, ResourceBusy
from formalchemy import FieldSet, Grid, ValidationError, Field

DEBUG = True
SECRET_KEY = 'development key'


app = Flask(__name__) #pylint: disable=C0103
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
pool = ObjectPool() #pylint: disable=C0103

class IPAddressValidator(object):
    """ formalchemy Validator for ip and hostname addresses """
    validIpAddress = re.compile("""^(([0-9]|[1-9][0-9]|1[0-9]{2}|
                                2[0-4][0-9]|25[0-5])\.)
                                {3}([0-9]|[1-9][0-9]|1[0-9]{2}|
                                2[0-4][0-9]|25[0-5])$""",
                                re.VERBOSE)
    
    validHostname = re.compile("""^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*
                                    [a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z]
                                    [A-Za-z0-9\-]*[A-Za-z0-9])$""",
                               re.VERBOSE)
    def __call__(self, value):
        if not ( self.validHostname.match(value) or
                 self.validIpAddress.match(value)):
            raise ValidationError('Not a valid IP or hostname address')

IPAddressValidator = IPAddressValidator() #pylint: disable=C0103

class MacAddressValidator(object):
    """ formalchemy Validator for mac addresses """
    validMACAddress = re.compile("""^([a-f0-9]{2}:){5}([a-f0-9]{2})$""")

    def __call__(self, value):
        if not ( self.validMACAddress.match(value) ):
            raise ValidationError('Not a valid MAC address \
                [i.e. 00:00:ff:ab:cc:32]')

MacAddressValidator = MacAddressValidator() #pylint: disable=C0103,R0903

from formalchemy import TextAreaFieldRenderer
class LineRenderer(TextAreaFieldRenderer):
    """ Render TextArea with scrollable multiple html lines """
    def render_readonly(self, **kwargs):
        """render html for read only mode"""
        value = self.field.raw_value
        if value:
            value = value.replace("\n","<br />\n")
        else:
            value = ""
        kwargs = {'value':value}
        return '<div class="scroll">%(value)s</div>' % kwargs
    
class ResourceFieldSet(FieldSet):
    """ Form FieldSet to edit Resource"""
    def __init__(self, *arg, **kwargs):
        """Pre-configuration"""
        FieldSet.__init__(self, *arg, **kwargs)
        options = [self.ip_address.required().validate(IPAddressValidator),
                   self.type.required(),
                   self.location.textarea(size="25x10"),
                   self.mac_address.validate(MacAddressValidator)
                   ]
        self.configure(options=options)

@app.route('/edit/<resource_key>', methods=['GET', 'POST'])
def edit_resource(resource_key):
    """ Edit a Resource from the Pool """
    if resource_key:
        obj = pool.session.query(Resource).get(resource_key)
    else:
        obj = Resource()
    form = ResourceFieldSet(obj)

    if request.method == 'POST':
        data = dict(request.form.items())

        # fix partial data add/editing
        data_dict = form.to_dict(as_string=True)
        data_dict.update(data)

        form = ResourceFieldSet(obj, data=data_dict)
        if form.validate():
            form.sync()
            pool.addResource(obj)
            flash("Resources Edited" if resource_key else "Resources Added" )
            return redirect(url_for('show_all_resources'))
    context = {
        'form': form,
        'item': obj
    }
    template_name = 'edit_resource.html' if resource_key \
        else 'add_resource.html'
    
    return render_template(template_name, **context)

@app.route('/add', methods=['GET', 'POST'])
def add_resource():
    """ Adding a Resource to the pool """

    return edit_resource(None)

@app.route('/delete/<res_id>', methods=['GET'])
def delete_resource(res_id):
    """ Delete a Resource from pool """

    pool.deleteResource(id=res_id)
    flash("Resource Deleted")
    return redirect(url_for('show_all_resources'))

@app.route('/retrieve/<platform>', methods=['GET', 'POST', 'PUT'])
def retrieve_resource(platform):
    """ Retrieve a Resource from pool and mark it as Used
        param taken_by is optional to state who took it and why """

    taken_by = None
    if "taken_by" in request.values:
        taken_by = request.values['taken_by']
    try:
        obj = pool.getResource(platform, taken_by)
        ret = ResourceFieldSet(obj).to_dict(with_prefix=False, as_string=True)
        ret['id'] = obj.id
    except ResourceBusy as exp:
        ret = dict(message=exp.message, id=None)
    return jsonify(ret)

@app.route('/platform_list', methods=['GET'])
def platform_list():
    """ List of all the platforms used """
    
    ret = dict(platforms=[platform.name for platform in pool.getPlatformList()])
    return jsonify(ret)

@app.route('/return/<res_id>', methods=['GET', 'POST', 'PUT'])
def return_resource(res_id):
    """ Return a Resource to the pool """

    pool.returnResource(id=res_id)
    flash("Resource Returned")
    return redirect(url_for('show_all_resources'))

@app.route('/')
def show_all_resources():
    """ Show all Resources from the pool """

    # TODO: move this configuration into a class
    grid = Grid(Resource, pool.allResourcesGenerator())
    grid.configure(options=[grid.location.with_renderer(LineRenderer)])
    grid.readonly = True
    grid.append(
        Field('',
              value=lambda item: '<a class="delete" href="/delete/%(id)d">[x]\
                </a><a href="/edit/%(id)d">[edit]</a>' % item.__dict__
            ).readonly()
    )
    return render_template('show_all_resources.html', grid=grid)

def main(): # pragma: no cover
    # TODO: add an option to export/import
    pool.emptyAllResources()
    try:
        pool.addResource(Resource("UPC", "10.64.62.111"))
        pool.addResource(Resource("GPVR", "10.64.62.23"))
    except IntegrityError:
        pass
    app.run()

if __name__ == "__main__":
    main() # pragma: no cover
    