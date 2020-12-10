FROM osgeo/gdal:ubuntu-small-3.2.0

RUN apt-get update -y && apt-get install -y python3-pip

# Install python dependencies
# Install everything for dev and test otherwise just core dependencies
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pip3 install --upgrade pip && pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile --dev

COPY ./app /app/app

WORKDIR /app
