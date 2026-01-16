# 启动指南（支持公网访问）

以下说明基于 `/home/chen/openai-chatkit-starter-app/chatkit` 目录，确保你已经安装好 Conda、nvm、Node 20.19 以及必要的依赖。

## 后端：使用已有 Conda 环境

如果你还没有 Conda 环境，可以复现以下流程：

1. 下载并安装 Miniconda（64 位 Linux），例如：
   ```bash
   cd ~
   curl -fsSLo Miniconda3.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   bash Miniconda3.sh -b -p ~/miniconda3
   ```
2. 激活 shell hooks 并接受官方 Terms of Service（只需做一次）：
   ```bash
   . ~/miniconda3/etc/profile.d/conda.sh
   conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
   conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
   ```
3. 创建 `chatkit` 环境，指定 Python 3.11，并把它激活：
   ```bash
   conda create -y -n chatkit python=3.11
   conda activate chatkit
   ```
4. 安装依赖（在项目内）：
   ```bash
   cd /home/chen/openai-chatkit-starter-app/chatkit/backend
   pip install -e .
   ```

如果你已经存在环境，请跳到下面的「进入项目并激活环境」步骤。

1. 进入项目并激活环境（每次新 shell 都要重复）：
   ```bash
   cd /home/chen/openai-chatkit-starter-app/chatkit
   . /home/chen/miniconda3/etc/profile.d/conda.sh
   conda activate chatkit
   ```

2. 确保 `OPENAI_API_KEY` 可用（脚本会自动从上层 `.env.local` 读取）：
   ```bash
   export OPENAI_API_KEY=sk-xxx
   ```

3. 如果需要通过代理/VPN 访问 OpenAI（例如 SOCKS5），请在同一个 shell 里导出代理变量：
   ```bash
   export HTTPS_PROXY=socks5://vpn-host:1080
   export HTTP_PROXY=socks5://vpn-host:1080
   export ALL_PROXY=socks5://vpn-host:1080
   ```
   `httpx`（因此 ChatKit）会自动使用这些变量。必要时可以额外设置 `HTTPX_PROXY`。

4. 直接用 Conda 环境里的 Python 启动后端，不走 `run.sh` 里的 `.venv` 创建流程：
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   这样后端会监听 `0.0.0.0`，可以通过服务器 IP 访问。

   > 若你仍想让 `run.sh` 使用 3.11：在另一个 shell 里把 PATH 置前再执行 `npm run backend`。

## 前端：独立运行

1. 载入 nvm 并切换到需要的 Node 版本：
   ```bash
   export NVM_DIR="/home/chen/.nvm"
   . "$NVM_DIR/nvm.sh"
   nvm use 20.19.0
   ```

2. 进入项目并安装依赖（只需一次）：
   ```bash
   cd /home/chen/openai-chatkit-starter-app/chatkit
   npm --prefix frontend install
   ```

3. 设定与后端一致的代理变量后启动 Vite：
   ```bash
   export HTTPS_PROXY=socks5://vpn-host:1080
   export HTTP_PROXY=socks5://vpn-host:1080
   export ALL_PROXY=socks5://vpn-host:1080
   npm --prefix frontend run dev
   ```
   Vite dev server 会自动代理 `/chatkit` 到 `http://localhost:8000`，此路径又被线上的 `uvicorn` 服务代理到 OpenAI。

## 同时暴露在公网

- 确保 `uvicorn` 用 `--host 0.0.0.0 --port 8000` 启动，后端即可通过 `http://<服务器IP>:8000/chatkit` 访问。
- 如果你要通过公网直接访问前端，请设置环境变量 `VITE_CHATKIT_API_URL=http://<服务器IP>:8000/chatkit`，然后在 `frontend` 目录运行 `npm run dev`（或构建后部署）。
- 确保服务器的安全组/防火墙开放 3000（前端）和 8000（后端）端口，或只开放 3000 并使用反向代理将 `/chatkit` 转发到本地 8000。
- 由于你已经在 OpenAI 平台的域名白名单中登记了 `117.72.15.209`，请在运行前端/dev server 前导出：
  ```bash
  export VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_696a0b4a62d481908b0444d9d8346543001d132fa9d49ac8
  ```
- 不要忘记把 `VITE_CHATKIT_API_URL` 指向你公网后端地址（`http://117.72.15.209:8000/chatkit`）。

## 额外说明

- `run.sh` 现在默认监听 `0.0.0.0:8000`，所以 `npm run dev` 也支持公网访问，只要上述环境变量设置完毕即可。
- 若你使用 ChatKit 的 `openai-chatkit` 包，请参考其配置要求（包括 `OPENAI_API_KEY`、域名 key 等）。

