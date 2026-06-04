# Build Stage
FROM python:3.11-slim

RUN pip install --no-cache-dir atheris

ADD . /src
WORKDIR /src
RUN pip install --no-cache-dir ./pkgs/pyhanko-certvalidator ./pkgs/pyhanko

CMD ["/src/mayhem/fuzz_pdf.py"]
