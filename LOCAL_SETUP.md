# SceneForge Animate — Local Mode

## Windows

1. Open PowerShell in the repository folder.
2. Switch to the SceneForge branch:
   ```powershell
   git checkout sceneforge-v3
   git pull
   ```
3. Run:
   ```powershell
   .\run.bat
   ```
4. On the first run, SceneForge creates `server/.env` and opens it in Notepad.
5. Fill in:
   ```env
   DEEPSEEK_API_KEY=...
   QWEN_API_KEY=sk-ws-...
   MESHY_API_KEY=...
   ```
6. Save the file and run `run.bat` again.
7. Open `http://127.0.0.1:8000`.

## macOS / Linux

```bash
git checkout sceneforge-v3
git pull
chmod +x run.sh
./run.sh
```

On first launch, edit `server/.env`, then run `./run.sh` again.

## What local mode changes

The browser no longer calls DeepSeek, Qwen/DashScope, or Meshy with your real API keys. The local FastAPI server reads keys from `server/.env` and forwards requests server-side. This removes the Qwen browser CORS problem and keeps provider keys out of browser storage.

## Health check

Open:

`http://127.0.0.1:8000/health`

You should see each configured provider as `true`.
