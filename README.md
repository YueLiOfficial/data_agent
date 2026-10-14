## 1.1. 项目代码说明

- `data-agent`：后端项目
- `data-agent_frontend`：前端项目

## 1.3. 构建知识库

- 进入后端项目目录data-agent，运行构建脚本`app/scripts/build_meta_knowledge.py`

- 先删除项目中的.venv和.idea

  ```
  ...\data-agent> uv sync
  ...\data-agent> .venv\Scripts\python -m app.scripts.build_meta_knowledge
  ```

## 1.4. 运行后端项目

- 进入后端项目目录data-agent，运行启动脚本`main.py`

  ```
  ...\data-agent>.venv\Scripts\python -m main
  ```

  

## 1.5. 运行前端项目

- 进入前端项目目录data-agent_frontend，执行启动命令

  ```
  ...\data-agent_frontend>npm run dev
  ```

  

## 1.6. 访问测试

- 浏览器上访问： http://127.0.0.1:5173/
- 搜索相关问题
  - 华北地区销售总额
  - 2025年各地区平均销售额
  - 各个地区iPhone去年卖了多少钱