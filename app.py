from flask import Flask, render_template, request, redirect, url_for
from funcs import *
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, StringField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
# import os
# import boto3

# dynamodb = boto3.resource('dynamodb')
app = Flask(__name__)
app.config['SECRET_KEY'] = "SECRET_KEY"
Bootstrap(app)
# sns = boto3.resource('sns')
# topic = 'arn:aws:sns:us-east-1:643020469822:Seattle-911-message'


df = pd.read_csv('static/df_72hr.csv')
geojson_df = create_geojson_df_csv('static/seattle_neighborhoods.geojson')
neighborhood_list = create_neighborhood_list(geojson_df)


class CreateMapForm(FlaskForm):
    incident = SelectField('Incident Type', choices=get_incident_list())
    neighborhood = SelectField('Neighborhood', choices=neighborhood_list)
    submit = SubmitField("Submit")


class CreateContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    message = StringField("Message", validators=[DataRequired()])
    submit = SubmitField("Send Message")


@app.route('/', methods=['GET', 'POST'])
def index():
    form = CreateMapForm()
    form2 = CreateContactForm()
    incident_list = get_incident_list()
    if form2.validate_on_submit():
        # message = create_sns_message(form2.name.data, form2.email.data, form2.message.data)
        # publish_sns_message(topic, message)
        return redirect(url_for('index'))
    if request.method == 'POST':
        m = create_incident_map(form.incident.data, form.neighborhood.data, df, geojson_df)
        m = m._repr_html_()
        return render_template('index.html', form=form, form2=form2, map=m,
                               incident_list=incident_list,
                               neighborhood_list=neighborhood_list)
    m = create_incident_map('All Incidents', 'Entire City', df, geojson_df)
    m = m._repr_html_()
    return render_template('index.html', form=form, form2=form2, map=m,
                           incident_list=incident_list,
                           neighborhood_list=neighborhood_list)


# @app.route('/favicon.ico')
# def favicon():
#     return send_from_directory(os.path.join(app.root_path, 'static'),
#                                'favicon.ico',
#                                mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run()
