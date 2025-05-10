FROM python:3.11-slim

WORKDIR /app

# Copy the built package (whl or tar.gz)
COPY dist/agent1-0.1.0-py3-none-any.whl .
#COPY dist/agent1-0.1.0.tar.gz .
# Install it
RUN pip install agent1-0.1.0-py3-none-any.whl

# todo check what to run here, agent1?
CMD ["agent1-0.1.0-py3-none-any"]
