# telegram github release bot

## 要求

-   带有 HTTPS 的域名
-   安装有 Docker、Docker Compose 的服务器

### 获取一个带有 HTTPS 的域名

#### Serveo

对于良好的网络环境，可以使用 serveo 进行代理：

```bash
ssh -R 80:localhost:8000 serveo.net
```

若是成功，会返回：

```bash
Forwarding HTTP traffic from https://<随机域名>.serveo.net
```

这个域名会映射本地 `localhost:8000` 地址到它给出的域名，可以使用这个域名来设置你的 Webhook。

#### cloudflare tunnel

对于国内的网络环境来说，很有可能是连不上 Serveo 的，所以只能另求他法，可以使用 ngrok 或是 cloudflare、frp 等工具。ngrok 是 serveo 灵感来源之一，同样不需要自备域名，但是如果环境里设置了代理就不能使用。至于其他工具就不一一介绍了。

因为我已经有域名了，所以是用的 cloudflare tunnel，它可以让我在开发和生产都不需要去手动配置 HTTPS。

**注意下文所指的 cloudflare tunnel 均是运行在 Docker 内。**

修改下面命令中的 `<TOKEN>` 值为 cloudflare tunnel 创建隧道时给出的 Token：

```bash
docker run -dit \
    --network host \
    --restart unless-stopped \
    --pull always \
    --name cf-tunnel \
    cloudflare/cloudflared:latest tunnel --no-autoupdate run --token <TOKEN>
```

其中使用 `--network host` 指定该容器使用主机网络。

而后在 cloudflare tunnel 添加一个 Public hostnames，subdomain 指定 `telegram-github-release-bot`，URL 使用 `localhost:8000` 就行，8000 端口是 Uvicorn 的默认启动端口。

## 开发

项目使用 3.11 进行开发，建议在 3.11 版本或是更高版本进行开发。

### 安装依赖管理器

项目依赖使用 PDM 进行管理，所以需要先安装 PDM：

```bash
pip install -U pdm
```

### 安装依赖

对于开发者来说，应该选择带有开发时依赖的安装方式：

```bash
pdm install -dv
```

### 使用带有依赖的虚拟环境

PDM 安装依赖时会检查当前目录下是否有虚拟环境，如果有，则使用已有的虚拟环境，如果没有，则创建一个虚拟环境。这里假设你事先没有创建虚拟环境，如果已经创建并使用了，可以跳过这一步。

```bash
pdm use -f .venv
```

### 创建开发环境配置文件

项目开发时依赖一些环境变量，可以参考 `.env.dev.example` 示例配置自己的环境变量：

```bash
cp ./.env.dev.example ./.env.dev
```

复制完成后记得填写其中缺少的值，那些都是必要的环境变量。

### 启动开发服务器

```bash
uvicorn src.main:app --reload
```

等待启动完成后，可以通过 <http://localhost:8000> 或是你那带有 HTTPS 的域名访问。

## 部署

项目使用 Docker Compose 进行部署。

### 创建生产环境配置文件

项目开发时依赖一些环境变量，可以参考 `.env.prod.example` 示例配置自己的环境变量：

```bash
cp ./.env.prod.example ./.env.prod
```

复制完成后记得填写其中缺少的值，那些都是必要的环境变量。

### 启动

#### 通过可访问主机网络的 Cloudflare Tunnel 进行部署

如果已经使用 cloudflare tunnel 并且允许 cloudflare tunnel 访问主机的网络，那么可以这样：

1. 停止掉开发服务器（如果启动了的话）
2. 取消 `./compose.yaml` 文件第 35-36 行的注释
3. 执行 `docker compose up --build telegram-github-release-bot -d`
4. 使用 `docker compose logs -tf` 查看是否启动完毕
5. 确定启动完毕后，再确定你那带有 HTTPS 的域名是否指向了正在运行的服务器（访问它看看是否已经如预期般）
6. 使用 `docker compose exec telegram-github-release-bot python set_webhook.py` 设置机器人的 webhook url

#### 通过带有 Container Network 的 Cloudflare Tunnel 进行部署

如果你的 cloudflare tunnel 访问不了主机网络，但是拥有自己的 container network，那么可以手动建立 `compose.yaml` 内的 django-ptb-proxy service 与 cloudflare tunnel 的 container network 的连接。

作为启动的步骤示例：

1. 执行 `docker compose up --build telegram-github-release-bot -d`
2. 使用 `docker compose logs -tf` 查看是否启动完毕
3. 确定启动完毕后，再确定你那带有 HTTPS 的域名是否指向了正在运行的服务器（访问它看看是否已经如预期般）
4. 将你的 cloudflare tunnel 的 container network 与 telegram-github-release-bot service 进行连接：

    ```bash
    docker network connect <cloudflare tunnel network name> telegram-github-release-bot
    ```

5. 在 cloudflare tunnel 修改前面添加的 Public hostnames，subdomain 不需要改，URL 改为 `telegram-github-release-bot:80`，80 端口是 Gunicorn 的监听端口
