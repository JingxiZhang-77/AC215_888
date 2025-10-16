🐳 Docker Commands Reference

1. Build the Image

```bash
docker build -t prompt_chaining -f Dockerfile .
```

2. Initiate the Container
```bash
docker run --rm -ti \
-v "$(pwd):/app" \
-v "$(pwd)/../../secrets:/secrets" \
prompt_chaining
```