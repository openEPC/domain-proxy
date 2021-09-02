ARG ENV=standard
FROM python:3.9.2-slim-buster as standard-version

COPY db_service/config.py db_service/models.py db_service/session_manager.py db_service/db_initialize.py /db_service/
COPY db_service/tests /db_service/tests
COPY mappings /mappings
COPY protobufs /protobufs
COPY test_runner /test_runner
COPY fixtures /fixtures

WORKDIR /test_runner
RUN pip3 install --upgrade pip --no-cache-dir -r requirements.txt
RUN python -m grpc_tools.protoc -I ../protobufs/requests --python_out=. --grpc_python_out=. ../protobufs/requests/requests.proto
RUN python -m grpc_tools.protoc -I ../protobufs/active_mode --python_out=. --grpc_python_out=. ../protobufs/active_mode/active_mode.proto

FROM ${ENV}-version as final
ENV PYTHONPATH=$PYTHONPATH:/

ENTRYPOINT ["python"]