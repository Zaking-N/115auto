# 构建阶段
FROM python:3.9-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# 运行阶段
FROM python:3.9-slim

WORKDIR /app

# 从构建阶段复制已安装的包
COPY --from=builder /root/.local /root/.local
COPY . .

# 确保Python可以找到用户安装的包
ENV PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/app

# 创建非root用户
RUN useradd -m appuser && \
    chown -R appuser:appuser /app && \
    mkdir -p /data && \
    chown -R appuser:appuser /data

USER appuser

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]